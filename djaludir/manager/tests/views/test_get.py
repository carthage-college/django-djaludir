from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from djtools.utils.logging import seperator
from djtools.utils.test import create_test_user


class ManagerViewsGETTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.password = settings.TEST_USER_PASSWORD
        self.user = create_test_user()

    def auth(self):
        login = self.client.login(
            username=self.user.username, password=self.password
        )
        self.assertTrue(login)

    def test_display(self):

        print("\n")
        print("display alumna data")

        self.auth()

        earl = reverse('manager_alum_display', args=[self.user.id])
        response = self.client.get(earl)
        print("URL:")
        print(response.request['PATH_INFO'])
        self.assertEqual(response.status_code, 200)

    def test_search(self):

        print("\n")
        print("search for alumni")

        self.auth()

        earl = reverse('manager_search')
        response = self.client.get(earl)
        print("URL:")
        print(response.request['PATH_INFO'])
        self.assertEqual(response.status_code, 200)

    def test_edit(self):

        print("\n")
        print("edit alumna data")

        self.auth()

        earl = reverse('manager_user_edit', args=[self.user.id])
        response = self.client.get(earl)
        print("URL:")
        print(response.request['PATH_INFO'])
        self.assertEqual(response.status_code, 200)

    def test_message(self):

        print("\n")
        print("send a message to alumna")

        self.auth()

        earl = reverse('message_user', args=[self.user.id])
        response = self.client.get(earl)
        print("URL:")
        print(response.request['PATH_INFO'])
        self.assertEqual(response.status_code, 200)


    def test_search_activity(self):

        print("\n")
        print("search activity")

        self.auth()

        earl = reverse('search_activity')
        response = self.client.get(earl)
        print("URL:")
        print(response.request['PATH_INFO'])
        self.assertEqual(response.status_code, 200)



