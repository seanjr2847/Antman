import os
from django.test import TestCase
from django.conf import settings


class UserTestCase(TestCase):
    """
    사용자 모델(User)이 올바르게 구성되었는지 테스트하는 테스트 케이스
    """

    def test_user_model(self):
        """
        사용자 모델이 올바르게 구성되었는지 확인
        """
        self.assertEqual(settings.AUTH_USER_MODEL, 'users.User')
