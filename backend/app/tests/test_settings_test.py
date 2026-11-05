import importlib
import os
from unittest import mock

import socketio
from django.conf import settings
from django.test import SimpleTestCase

from backend.app import settings_test, sockets

PG_ENV = {
    "TEST_DATABASE": "postgres",
    "POSTGRES_NAME": "ci_db",
    "POSTGRES_USER": "ci_user",
    "POSTGRES_PASSWORD": "ci_pw",
    "POSTGRES_HOST": "db.example",
    "POSTGRES_PORT": "6543",
}


def reload_settings_module(env, remove=()):
    """Re-execute settings_test.py under a patched environment.

    This only re-runs the module; it does not change django.conf.settings.
    """
    with mock.patch.dict(os.environ, env):
        for key in remove:
            os.environ.pop(key, None)
        return importlib.reload(settings_test)


class SettingsTestModuleTests(SimpleTestCase):
    def tearDown(self):
        # Restore the module to what the real environment produces.
        importlib.reload(settings_test)

    def test_default_is_sqlite_in_memory_even_if_postgres_host_is_set(self):
        # .env sets POSTGRES_HOST=postgres for Docker; that must not flip the DB.
        module = reload_settings_module(
            {"POSTGRES_HOST": "postgres"}, remove=["TEST_DATABASE"]
        )
        self.assertEqual(
            module.DATABASES["default"],
            {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        )

    def test_test_database_postgres_reads_postgres_env(self):
        module = reload_settings_module(PG_ENV)
        self.assertEqual(
            module.DATABASES["default"],
            {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "ci_db",
                "USER": "ci_user",
                "PASSWORD": "ci_pw",
                "HOST": "db.example",
                "PORT": "6543",
            },
        )


class TestSettingsRedisTests(SimpleTestCase):
    def test_redis_url_is_none(self):
        self.assertIsNone(settings.REDIS_URL)

    def test_module_level_server_uses_in_memory_manager(self):
        self.assertIs(type(sockets.sio.manager), socketio.AsyncManager)
