from rest_framework.test import APITestCase
from rest_framework import status


# Create your tests here.
class StatusVersionTestCase(APITestCase):
    def setUp(self):
        pass

    def test_get_status_version(self):
        """GET /status/version should return the current version and project name"""
        response = self.client.get('/status/version')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['env'], 'local')
        self.assertEqual(response.data['name'], 'arcv2_platform')
