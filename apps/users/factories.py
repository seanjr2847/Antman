"""
사용자 앱을 위한 Factory 클래스 모음
"""
import factory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker('ko_KR')  # 한국어 로케일 사용

class UserFactory(factory.django.DjangoModelFactory):
    """사용자 모델을 위한 팩토리 클래스"""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True
    is_staff = False
    is_superuser = False

class AdminFactory(UserFactory):
    """관리자 사용자 모델을 위한 팩토리 클래스"""
    
    username = factory.Sequence(lambda n: f'admin_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    is_staff = True
    is_superuser = True
