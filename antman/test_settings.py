"""
테스트 환경을 위한 Django 설정 파일입니다.
"""

from .settings import *

# 테스트 환경에서는 DEBUG를 True로 설정
DEBUG = True

# 테스트용 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# 테스트 시 비밀번호 해싱 속도 향상
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 테스트 미디어 저장 경로
MEDIA_ROOT = BASE_DIR / 'test_media'

# 테스트 캐시 설정
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 테스트 이메일 백엔드
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 테스트 템플릿 캐싱 비활성화
for template in TEMPLATES:
    # app_dirs와 loaders가 충돌하는 문제 해결
    app_dirs = template.get('APP_DIRS', False)
    if app_dirs:
        template['APP_DIRS'] = False
    
    # 템플릿 로더 설정
    template['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]

# 테스트에서 CSRF 검증 비활성화
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'django.middleware.csrf.CsrfViewMiddleware']
MIDDLEWARE.append('django.middleware.csrf.CsrfViewMiddleware')

# 테스트 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}
