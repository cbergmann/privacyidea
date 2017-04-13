"""
This test file tests the lib.usercache

The lib.usercache.py only depends on the database model
"""

from .base import MyTestCase
from privacyidea.lib.resolver import (save_resolver, delete_resolver)
from privacyidea.lib.realm import (set_realm, delete_realm)
from privacyidea.lib.user import (User, get_username)
from privacyidea.lib.usercache import (get_expiration_delta_from_config,
                                       cache_username, delete_user_cache)
from privacyidea.lib.config import set_privacyidea_config
from datetime import timedelta
from datetime import datetime
from privacyidea.models import UserCache


class UserCacheTestCase(MyTestCase):
    """
    Test the user on the database level
    """
    PWFILE = "tests/testdata/passwd"
    resolvername1 = "resolver1"
    realm1 = "realm1"
    username = "root"
    uid = "0"

    def _create_realm(self):

        rid = save_resolver({"resolver": self.resolvername1,
                               "type": "passwdresolver",
                               "fileName": self.PWFILE,
                               "type.fileName": "string",
                               "desc.fileName": "The name of the file"})
        self.assertTrue(rid > 0, rid)
        rid = set_realm(realm=self.realm1, resolvers=[self.resolvername1])
        self.assertTrue(rid > 0, rid)

    def _delete_realm(self):
        delete_realm(self.realm1)
        delete_resolver(self.resolvername1)

    def test_00_set_config(self):
        set_privacyidea_config("usercache.expirationSeconds", 60)

        exp_delta = get_expiration_delta_from_config()
        self.assertEqual(exp_delta, timedelta(seconds=60))

    def test_01_get_username_from_cache(self):
        # If a username is already contained in the cache, the function
        # lib.user.get_username will return the cache value
        username = "cached_user"
        realm = "realm1"
        resolver = "resolver1"
        uid = "1"

        expiration_delta = get_expiration_delta_from_config()
        r = UserCache(username, realm, resolver, uid,
                      expiration=datetime.now() + expiration_delta).save()
        u_name = cache_username(get_username, uid, resolver)
        self.assertEqual(u_name, username)

        # A non-existing user is not in the cache and returns and empty username
        u_name = cache_username(get_username, uid, "resolver_does_not_exist")
        self.assertEqual(u_name, "")

    def test_02_get_resolvers(self):
        # create realm
        self._create_realm()
        # delete user_cache
        r = delete_user_cache()
        self.assertTrue(r >= 0)

        # The username is not in the cache. It is fetched from the resolver
        # At the same time the cache is filled. Implicitly we test the
        # get_resolvers!
        user = User(self.username, self.realm1)
        self.assertEqual(user.login, self.username)

        # delete the resolver
        self._delete_realm()

        # the username is fetched from the cache
        u_name = get_username(self.uid, self.resolvername1)
        self.assertEqual(u_name, self.username)

        # delete the cache
        r = delete_user_cache()

        # try to fetch the username. It is not in the cache and the
        # resolver does not exist anymore.
        u_name = get_username(self.uid, self.resolvername1)
        self.assertEqual(u_name, "")

    def test_03_get_identifiers(self):
        # create realm
        self._create_realm()
        # delete user_cache
        r = delete_user_cache()
        self.assertTrue(r >= 0)

        # The username is not in the cache. It is fetched from the resolver
        # At the same time the cache is filled. Implicitly we test the
        # get_resolvers!
        user = User(self.username, self.realm1, self.resolvername1)
        uids = user.get_user_identifiers()
        self.assertEqual(user.login, self.username)

        # delete the resolver
        self._delete_realm()

        # the username is fetched from the cache
        u_name = get_username(self.uid, self.resolvername1)
        self.assertEqual(u_name, self.username)

        # delete the cache
        r = delete_user_cache()

        # try to fetch the username. It is not in the cache and the
        # resolver does not exist anymore.
        u_name = get_username(self.uid, self.resolvername1)
        self.assertEqual(u_name, "")
