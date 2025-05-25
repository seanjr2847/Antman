# Antman 프로젝트

## 개요

Antman은 Django 기반의 확장 가능한 웹 애플리케이션 프레임워크입니다. 코드 생성, 오류 처리, 미들웨어 및 다양한 유틸리티 기능을 제공하여 빠르고 안정적인 웹 애플리케이션 개발을 지원합니다.

### 주요 기능

- **코드 생성**: Django 모델, 뷰, 시리얼라이저 등의 자동 생성
- **오류 처리**: 통합된 예외 처리 및 로깅 시스템
- **미들웨어**: 요청/응답 로깅, 성능 모니터링, 보안 강화
- **코드 품질**: 자동화된 코드 포맷팅 및 린팅
- **CI/CD 파이프라인**: 자동화된 테스트, 빌드, 배포 과정

# 설치

### 요구 사항

- Python 3.10+
- Docker 및 Docker Compose
- Git

### 기본 설치

```bash
# 저장소 클론
git clone https://gitlab.com/your-organization/antman.git
cd antman

# 가상 환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발용 의존성

# 환경 설정
cp .env.example .env
# .env 파일을 필요에 맞게 수정

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
```

### Docker를 이용한 설치

```bash
# 개발 환경
docker-compose up -d

# 스테이징 환경
docker-compose -f docker-compose.staging.yml up -d

# 프로덕션 환경
docker-compose -f docker-compose.production.yml up -d
```

# 사용법

### 기본 사용법

1. Django 관리자 페이지: `http://localhost:8000/admin/`
2. API 엔드포인트: `http://localhost:8000/api/`
3. 헬스 체크: `http://localhost:8000/health/`

## 사용 지침서

### 1. 코드 생성 기능 사용법

Antman은 반복적인 코드를 자동으로 생성하는 강력한 도구를 제공합니다. 다음은 주요 코드 생성 기능에 대한 상세 사용법입니다.

#### 1.1 모델 생성기 (ModelGenerator)

```python
from core.code_generation.model_generator import ModelGenerator

# Django 모델 자동 생성
generator = ModelGenerator(config={
    "model_name": "Product",
    "app_name": "products",  # 모델이 속할 앱 이름
    "fields": [
        {"name": "name", "type": "CharField", "max_length": 100},
        {"name": "price", "type": "DecimalField", "max_digits": 10, "decimal_places": 2},
        {"name": "description", "type": "TextField", "null": True, "blank": True},
        {"name": "category", "type": "ForeignKey", "to": "Category", "on_delete": "CASCADE"}
    ],
    "meta_options": {  # 모델 Meta 클래스 옵션
        "verbose_name": "제품",
        "verbose_name_plural": "제품들",
        "ordering": ["-created_at"],
        "indexes": ["name", "category"]
    },
    "include_timestamps": True,  # created_at, updated_at 필드 추가
    "include_str_method": True  # __str__ 메서드 추가
})

# 모델 코드 생성
model_code = generator.generate()

# 파일로 저장 (선택사항)
generator.save(model_code, filename="models.py")
```

#### 1.2 뷰 생성기 (ViewGenerator)

```python
from core.code_generation.view_generator import ViewGenerator

# Django 뷰 자동 생성
view_generator = ViewGenerator(config={
    "model": "Product",
    "app_name": "products",
    "view_type": "viewset",  # 'viewset', 'apiview', 'function', 'class'
    "operations": ["list", "retrieve", "create", "update", "delete"],
    "authentication": True,
    "permission_classes": ["IsAuthenticated"],
    "filtering": {
        "fields": ["name", "price", "category"],
        "search_fields": ["name", "description"]
    },
    "pagination": True,
    "nested_routes": [
        {"model": "Review", "relation": "reviews", "operations": ["list", "create"]}
    ]
})

# 뷰 코드 생성
view_code = view_generator.generate()
view_generator.save(view_code, filename="views.py")
```

#### 1.3 시리얼라이저 생성기 (SerializerGenerator)

```python
from core.code_generation.serializer_generator import SerializerGenerator

# DRF 시리얼라이저 자동 생성
serializer_generator = SerializerGenerator(config={
    "model": "Product",
    "app_name": "products",
    "fields": "__all__",  # 모든 필드 포함 또는 특정 필드 리스트
    "depth": 1,  # 가져오기 깊이
    "nested_serializers": [
        {"model": "Category", "fields": ["id", "name"]}
    ],
    "validation": {  # 유효성 검사 규칙
        "name": {"min_length": 3, "max_length": 100},
        "price": {"min_value": 0}
    },
    "read_only_fields": ["created_at", "updated_at"]
})

# 시리얼라이저 코드 생성
serializer_code = serializer_generator.generate()
serializer_generator.save(serializer_code, filename="serializers.py")
```

#### 1.4 전체 CRUD 애플리케이션 생성

```python
from core.code_generation.app_generator import AppGenerator

# 전체 CRUD 애플리케이션 생성
app_generator = AppGenerator(config={
    "app_name": "products",
    "models": [
        {
            "name": "Category",
            "fields": [
                {"name": "name", "type": "CharField", "max_length": 50},
                {"name": "description", "type": "TextField", "blank": True}
            ]
        },
        {
            "name": "Product",
            "fields": [
                {"name": "name", "type": "CharField", "max_length": 100},
                {"name": "price", "type": "DecimalField", "max_digits": 10, "decimal_places": 2},
                {"name": "description", "type": "TextField", "null": True},
                {"name": "category", "type": "ForeignKey", "to": "Category", "on_delete": "CASCADE"}
            ]
        }
    ],
    "api_type": "rest",  # 'rest' 또는 'graphql'
    "authentication": True,
    "include_tests": True,
    "include_docs": True,
    "include_admin": True
})

# 전체 애플리케이션 코드 생성 및 저장
app_generator.generate_app()
```

### 2. 오류 처리 시스템 사용법

Antman은 포괄적인 오류 처리 시스템을 제공합니다. 이를 통해 애플리케이션 전체에서 예외를 일관되게 처리하고, 로깅할 수 있습니다.

#### 2.1 기본 예외 사용법

```python
from core.error_handling.base import AntmanBaseException
from core.error_handling.exceptions import ValidationError, AuthenticationError, ResourceNotFoundError

# 사용자 정의 예외 발생
if not valid_data:
    raise ValidationError(
        message="데이터가 유효하지 않습니다.",
        code="invalid_data",
        extra_data={'fields': ['name', 'email']}
    )

# 예외 처리
try:
    # 코드 실행
    process_data(data)
except ValidationError as e:
    # 유효성 검사 오류 처리
    logger.warning(f"유효성 오류: {str(e)}")
    return JsonResponse(e.to_dict(), status=400)
except AuthenticationError as e:
    # 인증 오류 처리
    logger.error(f"인증 오류: {str(e)}")
    return JsonResponse(e.to_dict(), status=401)
except ResourceNotFoundError as e:
    # 리소스 찾을 수 없음 오류 처리
    logger.info(f"리소스 찾을 수 없음: {str(e)}")
    return JsonResponse(e.to_dict(), status=404)
except AntmanBaseException as e:
    # 기타 Antman 예외 처리
    logger.error(f"시스템 오류: {str(e)}")
    return JsonResponse(e.to_dict(), status=500)
except Exception as e:
    # 시스템 예외 처리
    logger.critical(f"처리되지 않은 예외: {str(e)}")
    return JsonResponse({'error': True, 'message': '서버 오류가 발생했습니다.'}, status=500)
```

#### 2.2 오류 핸들러 사용법

```python
from core.error_handling.handlers import ErrorHandler

# 오류 핸들러 생성
error_handler = ErrorHandler()

# 전역 오류 핸들링 등록
@error_handler.register(ValidationError)
def handle_validation_error(error, request=None):
    return JsonResponse(error.to_dict(), status=400)

# 오류 처리 사용
try:
    # 에러가 발생할 수 있는 코드
    result = process_data(data)
    return JsonResponse(result)
except Exception as e:
    # 등록된 핸들러로 오류 처리
    return error_handler.handle(e, request)
```

### 3. 미들웨어 시스템 사용법

Antman은 애플리케이션의 각 요청과 응답을 처리하기 위한 미들웨어 시스템을 제공합니다.

#### 3.1 요청 로깅 미들웨어 사용법

```python
# settings.py
MIDDLEWARE = [
    # ... 기존 미들웨어 ...
    'core.middleware.request_logging.RequestLoggingMiddleware',
]

# 설정 추가
LOGGING = {
    # ... 기존 로깅 설정 ...
    'handlers': {
        'request_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/requests.log',
        },
    },
    'loggers': {
        'request_logger': {
            'handlers': ['request_handler'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

#### 3.2 성능 모니터링 미들웨어 사용법

```python
# settings.py
MIDDLEWARE = [
    # ... 기존 미들웨어 ...
    'core.middleware.performance.PerformanceMonitoringMiddleware',
]

# 설정 추가
PERFORMANCE_THRESHOLD_MS = 500  # 500ms 이상 걸리는 요청 로깅
PERFORMANCE_MONITORING_ENABLED = True
```

#### 3.3 보안 헤더 미들웨어 사용법

```python
# settings.py
MIDDLEWARE = [
    # ... 기존 미들웨어 ...
    'core.middleware.security.SecurityHeadersMiddleware',
]

# 설정 추가
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self';",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}
```

#### 3.4 사용자 정의 미들웨어 구현

```python
# custom_middleware.py
from core.middleware.base import BaseMiddleware

class CustomMiddleware(BaseMiddleware):
    """사용자 정의 미들웨어 예제"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        # 초기화 코드
    
    def process_request(self, request):
        # 요청 처리
        self.logger.info(f"요청 처리: {request.path}")
        return None  # None을 반환하면 다음 미들웨어로 진행
    
    def process_response(self, request, response):
        # 응답 처리
        self.logger.info(f"응답 처리: {response.status_code}")
        return response  # 수정된 응답 반환
    
    def process_exception(self, request, exception):
        # 예외 처리
        self.logger.error(f"예외 발생: {str(exception)}")
        return None  # None을 반환하면 기본 예외 처리로 진행
```

### 4. 코드 품질 관리 시스템 사용법

Antman은 코드 품질을 일관되게 유지하기 위한 다양한 도구를 제공합니다.

#### 4.1 코드 포맷터 사용법

```python
from core.code_quality.formatter import CodeFormatter

# Python 코드 포맷팅
formatter = CodeFormatter()

# 파일 포맷팅
formatted_code = formatter.format_file('path/to/file.py')

# 문자열 포맷팅
code = """def example_function( a,b ):\n    return a+b"""
formatted_code = formatter.format_string(code)

# 디렉토리 포맷팅
formatter.format_directory('path/to/directory', recursive=True)
```

#### 4.2 코드 린터 사용법

```python
from core.code_quality.linter import CodeLinter

# 코드 린팅
linter = CodeLinter()

# 파일 린팅
issues = linter.lint_file('path/to/file.py')
for issue in issues:
    print(f"{issue.code}: {issue.message} at line {issue.line}")

# 디렉토리 린팅
all_issues = linter.lint_directory('path/to/directory', recursive=True)

# 코드 문자열 린팅
code = """import os, sys\nfor i in range(10):\n  print(i)"""
issues = linter.lint_string(code)
```

#### 4.3 코드 품질 관리자 사용법

```python
from core.code_quality.manager import CodeQualityManager

# 코드 품질 관리자 생성
manager = CodeQualityManager()

# 전체 작업 실행 (포맷팅, 린팅, import 정렬)
results = manager.run('path/to/directory', 
                     format_code=True, 
                     lint_code=True, 
                     sort_imports=True, 
                     fix_issues=True)

# 결과 요약 출력
manager.print_summary(results)

# HTML 보고서 생성
manager.generate_report(results, 'report.html')
```

### 5. CI/CD 파이프라인 사용법

Antman은 GitLab CI/CD를 통한 자동화된 테스트, 빌드, 배포 과정을 제공합니다.

#### 5.1 기본 파이프라인 사용법

`.gitlab-ci.yml` 파일이 이미 구성되어 있어 추가 설정 없이 사용할 수 있습니다. 다음은 각 단계에서 수행되는 작업입니다:

1. **Lint**: 코드 품질 검사 (Ruff, Black, isort)
2. **Test**: 단위 테스트 및 커버리지 결과 생성
3. **Build**: Docker 이미지 빌드 및 저장
4. **Security**: 코드 및 컨테이너 보안 스캔
5. **Deploy**: 스테이징/프로덕션 환경에 배포

#### 5.2 배포 스크립트 사용법

```bash
# 스테이징 환경에 배포
./scripts/deploy.sh staging

# 프로덕션 환경에 배포
./scripts/deploy.sh production

# 이전 버전으로 롤백
./scripts/rollback.sh production 1.2.3

# 데이터베이스 백업
./scripts/backup.sh production
```

### 6. 헬스 체크 및 모니터링 사용법

#### 6.1 헬스 체크 엔드포인트 활용

```bash
# 시스템 상태 확인
curl http://localhost:8000/health/

# 결과
{"status": "ok"}
```

#### 6.2 설정 예시

```python
# 로드 밸런서 구성 예시 (Nginx)
http {
    upstream app_servers {
        server web1:8000;
        server web2:8000;
        server web3:8000;
    }
    
    server {
        location / {
            proxy_pass http://app_servers;
        }
        
        # 헬스 체크
        location /health/ {
            proxy_pass http://app_servers/health/;
            health_check interval=30 fails=3 passes=2;
        }
    }
}
```

# 구성

### 프로젝트 구조

```
antman/
├── antman/           # 프로젝트 설정
├── apps/             # Django 애플리케이션
├── core/             # 코어 기능
│   ├── code_generation/  # 코드 생성 도구
│   ├── error_handling/   # 오류 처리 시스템
│   ├── middleware/       # 미들웨어
│   └── code_quality/     # 코드 품질 도구
├── docs/             # 문서
├── media/            # 미디어 파일
├── nginx/            # Nginx 설정
├── scripts/          # 배포 및 유틸리티 스크립트
├── static/           # 정적 파일
├── templates/        # HTML 템플릿
└── tests/            # 테스트 코드
```

### 설정 옵션

중요한 설정은 `.env` 파일에서 관리됩니다. 주요 설정 옵션은 다음과 같습니다:

- `DEBUG`: 디버그 모드 활성화 여부
- `SECRET_KEY`: Django 보안 키
- `DATABASE_URL`: 데이터베이스 연결 문자열
- `ALLOWED_HOSTS`: 허용된 호스트 목록

# 개발

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_system_integration.py

# 커버리지 보고서 생성
pytest --cov=.
```

### CI/CD 파이프라인

이 프로젝트는 GitLab CI/CD 파이프라인을 사용합니다. 주요 단계는 다음과 같습니다:

1. Lint: 코드 품질 검사
2. Test: 테스트 실행
3. Build: Docker 이미지 빌드
4. Security: 보안 스캔
5. Deploy: 배포

### 기여 가이드라인

1. 이슈 생성 또는 기존 이슈 선택
2. 새 브랜치 생성 (이슈 번호 포함)
3. 코드 작성 및 테스트
4. 커밋 메시지에 이슈 번호 포함
5. 풀 리퀘스트 생성

## 라이센스

이 프로젝트는 MIT 라이센스로 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
