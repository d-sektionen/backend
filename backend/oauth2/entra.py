"""The authorization-code flow for Entra login.

MSAL owns state, nonce, PKCE and token validation. Only the pending flow is
stored in the Django session; Graph tokens are used once to load the profile.
Each request gets its own MSAL client and in-memory token cache.
"""

import msal
from django.conf import settings

SCOPES = ["User.Read"]
# Reuse Identity's pending-flow keys so a login started before deployment can finish.
FLOW_KEY = "_auth_flow"
NEXT_KEY = "identity.web.next_link"


class LoginError(Exception):
    pass


def _client():
    if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
        raise LoginError("Microsoft login is not configured.")
    return msal.ConfidentialClientApplication(
        settings.MICROSOFT_CLIENT_ID,
        client_credential=settings.MICROSOFT_CLIENT_SECRET,
        authority=settings.MICROSOFT_AUTHORITY,
        instance_discovery=False,
        timeout=30,
    )


def start_login(request, next_link):
    flow = _client().initiate_auth_code_flow(
        SCOPES,
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
        prompt="select_account",
    )
    if "error" in flow or not flow.get("auth_uri"):
        raise LoginError("Microsoft login could not be started.")
    flow[NEXT_KEY] = next_link
    request.session[FLOW_KEY] = flow
    return flow["auth_uri"]


def complete_login(request):
    # Consume the flow even on failure; a callback cannot be replayed.
    flow = request.session.pop(FLOW_KEY, None)
    if not flow:
        raise LoginError("Your login session has expired. Please sign in again.")
    try:
        result = _client().acquire_token_by_auth_code_flow(flow, request.GET.dict())
    except ValueError as exc:
        raise LoginError("Invalid login response. Please sign in again.") from exc
    if (
        "error" in result
        or not result.get("id_token_claims")
        or not result.get("access_token")
    ):
        raise LoginError("Microsoft login was not completed. Please sign in again.")
    return result, flow.get(NEXT_KEY, "/")
