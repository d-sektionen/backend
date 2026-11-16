from unittest.mock import Mock, patch
import json
import requests

from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from msal import ConfidentialClientApplication
from rest_framework_simplejwt.tokens import RefreshToken

from .entra import FLOW_KEY, NEXT_KEY


@override_settings(
    ALLOWED_HOSTS=["testserver", "medlem.d-sektionen.se"],
    MICROSOFT_REDIRECT_URI="http://localhost:8000/oauth2/callback",
)
class EntraLoginTests(TestCase):
    def setUp(self):
        self.user_count = User.objects.count()
        self.factory_patch = patch(
            "backend.oauth2.entra.msal.ConfidentialClientApplication"
        )
        self.factory = self.factory_patch.start()
        self.addCleanup(self.factory_patch.stop)
        self.msal = self.factory.return_value
        self.msal.initiate_auth_code_flow.return_value = {
            "auth_uri": "https://login.microsoftonline.com/authorize?state=expected",
            "state": "expected",
        }
        self.msal.acquire_token_by_auth_code_flow.return_value = {
            "access_token": "graph-token",
            "id_token_claims": {"preferred_username": "abcd12@student.liu.se"},
        }
        graph_patch = patch(
            "backend.oauth2.auth.get_me",
            return_value={
                "givenName": "Ada",
                "surname": "Lovelace",
                "mail": "ada@example.com",
            },
        )
        self.graph = graph_patch.start()
        self.addCleanup(graph_patch.stop)

    def begin(self, next_link="/account/"):
        return self.client.get("/oauth2/login", {"next": next_link})

    def callback(self):
        return self.client.get(
            "/oauth2/callback", {"state": "expected", "code": "code"}
        )

    def test_login_stores_flow_and_redirects_to_entra(self):
        response = self.begin()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, self.msal.initiate_auth_code_flow.return_value["auth_uri"]
        )
        self.assertEqual(self.client.session[FLOW_KEY][NEXT_KEY], "/account/")
        self.msal.initiate_auth_code_flow.assert_called_once_with(
            ["User.Read"],
            redirect_uri="http://localhost:8000/oauth2/callback",
            prompt="select_account",
        )

    def test_callback_updates_profile_and_sets_session_and_jwt_cookies(self):
        self.begin()
        response = self.callback()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/")
        user = User.objects.get(username="abcd12")
        self.assertEqual(
            (user.first_name, user.last_name, user.email),
            ("Ada", "Lovelace", "ada@example.com"),
        )
        self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))
        self.assertNotIn(FLOW_KEY, self.client.session)
        self.graph.assert_called_once_with("graph-token")
        for name in ("access_token", "refresh_token"):
            self.assertTrue(response.cookies[name]["httponly"])
            self.assertEqual(response.cookies[name]["samesite"], "Lax")
        self.assertEqual(response.cookies["refresh_token"]["path"], "/oauth2")
        self.assertNotIn("graph-token", str(dict(self.client.session)))

    def test_callback_without_flow_cannot_authenticate(self):
        self.assertEqual(self.callback().status_code, 400)
        self.msal.acquire_token_by_auth_code_flow.assert_not_called()
        self.assertEqual(User.objects.count(), self.user_count)

    def test_login_without_next_returns_to_root(self):
        self.client.get("/oauth2/login")
        self.assertEqual(self.callback().url, "/")

    def test_configuration_and_network_failures_do_not_start_a_flow(self):
        with override_settings(MICROSOFT_CLIENT_ID=None):
            self.assertEqual(self.begin().status_code, 400)
        self.factory.side_effect = requests.ConnectionError("offline")
        self.assertEqual(self.begin().status_code, 503)
        self.assertNotIn(FLOW_KEY, self.client.session)

    def test_callback_flow_is_consumed_after_failure(self):
        self.begin()
        self.msal.acquire_token_by_auth_code_flow.side_effect = ValueError(
            "state mismatch"
        )
        response = self.callback()
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(FLOW_KEY, self.client.session)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertNotIn("access_token", response.cookies)
        self.assertEqual(self.callback().status_code, 400)
        self.msal.acquire_token_by_auth_code_flow.assert_called_once()

    def test_msal_rejects_a_real_flow_from_another_session_before_token_exchange(self):
        http = Mock()
        discovery = requests.Response()
        discovery.status_code = 200
        discovery._content = json.dumps(
            {
                "authorization_endpoint": "https://login.microsoftonline.com/tenant/authorize",
                "token_endpoint": "https://login.microsoftonline.com/tenant/token",
                "issuer": "https://login.microsoftonline.com/tenant/v2.0",
            }
        ).encode()
        http.get.return_value = discovery
        real_client = ConfidentialClientApplication(
            "test-client",
            client_credential="secret",
            authority="https://login.microsoftonline.com/tenant",
            instance_discovery=False,
            http_client=http,
        )
        self.factory.return_value = real_client
        self.begin()
        flow = self.client.session[FLOW_KEY]
        response = self.client.get(
            "/oauth2/callback", {"state": "other-session", "code": "code"}
        )
        self.assertTrue(flow["state"])
        self.assertEqual(response.status_code, 400)
        http.post.assert_not_called()
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_provider_errors_and_incomplete_tokens_do_not_create_users(self):
        for result in (
            {"error": "access_denied"},
            {"access_token": "token"},
            {"id_token_claims": {"preferred_username": "abcd12@student.liu.se"}},
            {
                "access_token": "token",
                "id_token_claims": {"preferred_username": "outsider@example.com"},
            },
        ):
            with self.subTest(result=result):
                self.begin()
                self.msal.acquire_token_by_auth_code_flow.return_value = result
                self.assertEqual(self.callback().status_code, 400)
                self.assertEqual(User.objects.count(), self.user_count)
        self.graph.assert_not_called()

    def test_pending_flow_is_not_shared_between_browser_sessions(self):
        self.begin()
        stranger = Client()
        self.assertEqual(
            stranger.get(
                "/oauth2/callback", {"state": "expected", "code": "code"}
            ).status_code,
            400,
        )
        self.msal.acquire_token_by_auth_code_flow.assert_not_called()
        self.assertIn(FLOW_KEY, self.client.session)

    def test_redirects_are_validated_at_login_and_callback(self):
        for url in ("https://evil.example/", "//evil.example/", "javascript:alert(1)"):
            with self.subTest(url=url):
                self.begin(url)
                self.assertEqual(self.client.session[FLOW_KEY][NEXT_KEY], "/")
                # Simulate an old flow whose redirect predates this validation.
                session = self.client.session
                flow = session[FLOW_KEY]
                flow[NEXT_KEY] = url
                session[FLOW_KEY] = flow
                session.save()
                self.assertEqual(self.callback().url, "/")

    def test_existing_authenticated_session_survives_rejected_callback(self):
        user = User.objects.create_user("existing")
        self.client.force_login(user)
        self.assertEqual(self.callback().status_code, 400)
        self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))

    def test_refresh_rotates_and_blacklists_old_token(self):
        user = User.objects.create_user("existing")
        old = RefreshToken.for_user(user)
        self.client.cookies["refresh_token"] = str(old)
        response = self.client.post(
            "/oauth2/login/refresh", {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.cookies["refresh_token"].value, str(old))
        self.assertEqual(response.json(), {})
        self.assertEqual(
            self.client.post(
                "/oauth2/login/refresh", {}, content_type="application/json"
            ).status_code,
            200,
        )
        self.client.cookies["refresh_token"] = str(old)
        self.assertNotEqual(
            self.client.post(
                "/oauth2/login/refresh", {}, content_type="application/json"
            ).status_code,
            200,
        )

    def test_logout_is_local_and_clears_both_cookie_paths(self):
        user = User.objects.create_user("existing")
        self.client.force_login(user)
        self.client.cookies["refresh_token"] = str(RefreshToken.for_user(user))
        self.client.cookies["access_token"] = str(
            RefreshToken.for_user(user).access_token
        )
        response = self.client.post("/oauth2/logout?next=https://evil.example/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertEqual(response.cookies["refresh_token"]["path"], "/oauth2")
        self.assertEqual(response.cookies["refresh_token"]["max-age"], 0)
        self.assertEqual(response.cookies["access_token"]["path"], "/")
        self.msal.remove_account.assert_not_called()
