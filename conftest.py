"""
pytest 공통 fixture 및 설정을 위한 conftest.py 파일입니다.
"""
import os
import pytest

# Django가 설치된 경우에만 import
try:
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

# 테스트 데이터베이스 재사용 설정
@pytest.fixture(scope='session')
def django_db_setup():
    if not DJANGO_AVAILABLE:
        pytest.skip("Django not available")
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(settings.BASE_DIR, 'test_db.sqlite3'),
    }

# 인증된 클라이언트 fixture
@pytest.fixture
def authenticated_client(client, django_user_model):
    if not DJANGO_AVAILABLE:
        pytest.skip("Django not available")
    username = 'testuser'
    password = 'testpassword'
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client

# 관리자 클라이언트 fixture
@pytest.fixture
def admin_client(client, django_user_model):
    if not DJANGO_AVAILABLE:
        pytest.skip("Django not available")
    username = 'admin'
    password = 'adminpassword'
    user = django_user_model.objects.create_superuser(
        username=username, 
        password=password, 
        email='admin@example.com'
    )
    client.login(username=username, password=password)
    return client

# 테스트 후 미디어 파일 정리
@pytest.fixture(scope='function', autouse=True)
def cleanup_test_media():
    yield
    import shutil
    if os.path.exists(settings.MEDIA_ROOT):
        for item in os.listdir(settings.MEDIA_ROOT):
            path = os.path.join(settings.MEDIA_ROOT, item)
            if os.path.isfile(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
