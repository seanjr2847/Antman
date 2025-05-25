"""
사용자 모델 테스트
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.factories import UserFactory, AdminFactory

User = get_user_model()

class UserModelTest(TestCase):
    """사용자 모델 테스트 클래스"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.user = UserFactory.create(
            username='testuser',
            email='test@example.com'
        )
    
    def test_user_creation(self):
        """사용자 생성 테스트"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_user_str_method(self):
        """사용자 __str__ 메서드 테스트"""
        self.assertEqual(str(self.user), 'testuser')
    
    def test_user_password_hashing(self):
        """사용자 비밀번호 해싱 테스트"""
        self.assertTrue(self.user.check_password('password123'))
        self.assertFalse(self.user.check_password('wrongpassword'))
    
    def test_admin_user(self):
        """관리자 사용자 테스트"""
        admin = AdminFactory.create()
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


@pytest.mark.django_db
class UserModelPytestTest:
    """pytest를 사용한 사용자 모델 테스트 클래스"""
    
    def test_user_create(self):
        """사용자 생성 테스트 (pytest 방식)"""
        user = User.objects.create_user(
            username='pytestuser',
            email='pytest@example.com',
            password='testpass123'
        )
        assert user.username == 'pytestuser'
        assert user.email == 'pytest@example.com'
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_user_factory(self, db):
        """UserFactory 테스트"""
        user = UserFactory.create()
        assert User.objects.filter(username=user.username).exists()
