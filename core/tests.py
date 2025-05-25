import os
import unittest
import docker
import yaml
from django.test import TestCase
from django.conf import settings


class ProjectStructureTestCase(TestCase):
    """
    프로젝트 구조가 올바르게 설정되었는지 확인하는 테스트 케이스
    """

    def test_project_root_exists(self):
        """
        프로젝트 루트 디렉토리가 존재하는지 확인
        """
        base_dir = settings.BASE_DIR
        self.assertTrue(os.path.exists(base_dir), f"프로젝트 루트 디렉토리가 존재하지 않습니다: {base_dir}")
    
    def test_core_directories_exist(self):
        """
        핵심 디렉토리(apps, core, templates, static, media)가 존재하는지 확인
        """
        base_dir = settings.BASE_DIR
        required_dirs = ['apps', 'core', 'templates', 'static', 'media']
        
        for directory in required_dirs:
            dir_path = os.path.join(base_dir, directory)
            self.assertTrue(os.path.exists(dir_path), f"{directory} 디렉토리가 존재하지 않습니다.")
            self.assertTrue(os.path.isdir(dir_path), f"{directory}가 디렉토리가 아닙니다.")
    
    def test_app_directories_exist(self):
        """
        앱 디렉토리(users, projects)가 존재하는지 확인
        """
        apps_dir = os.path.join(settings.BASE_DIR, 'apps')
        required_apps = ['users', 'projects']
        
        for app in required_apps:
            app_path = os.path.join(apps_dir, app)
            self.assertTrue(os.path.exists(app_path), f"{app} 앱 디렉토리가 존재하지 않습니다.")
            self.assertTrue(os.path.isdir(app_path), f"{app}이(가) 디렉토리가 아닙니다.")
    
    def test_app_structure(self):
        """
        앱 구조가 올바른지 확인 (models.py, views.py, etc.)
        """
        apps_dir = os.path.join(settings.BASE_DIR, 'apps')
        required_apps = ['users', 'projects']
        required_files = ['__init__.py', 'models.py', 'views.py', 'tests.py', 'admin.py', 'apps.py']
        
        for app in required_apps:
            app_path = os.path.join(apps_dir, app)
            
            for file in required_files:
                file_path = os.path.join(app_path, file)
                self.assertTrue(os.path.exists(file_path), f"{app} 앱의 {file} 파일이 존재하지 않습니다.")
                self.assertTrue(os.path.isfile(file_path), f"{app} 앱의 {file}이(가) 파일이 아닙니다.")
    
    def test_python_packages(self):
        """
        apps와 core가 Python 패키지인지 확인 (__init__.py 존재)
        """
        base_dir = settings.BASE_DIR
        package_dirs = ['apps', 'core']
        
        for directory in package_dirs:
            init_file = os.path.join(base_dir, directory, '__init__.py')
            self.assertTrue(os.path.exists(init_file), f"{directory}의 __init__.py 파일이 존재하지 않습니다.")
            self.assertTrue(os.path.isfile(init_file), f"{directory}의 __init__.py가 파일이 아닙니다.")
    
    def test_gitignore_exists(self):
        """
        .gitignore 파일이 존재하는지 확인
        """
        gitignore_path = os.path.join(settings.BASE_DIR, '.gitignore')
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore 파일이 존재하지 않습니다.")
        self.assertTrue(os.path.isfile(gitignore_path), ".gitignore가 파일이 아닙니다.")
        
        # .gitignore 내용 확인 (최소한의 Python/Django 관련 항목 포함)
        with open(gitignore_path, 'r') as f:
            content = f.read()
            essential_patterns = {
                '*.pyc': ['*.pyc', '*.py[cod]'],  # *.pyc 또는 *.py[cod] 중 하나가 있어야 함
                '__pycache__': ['__pycache__'],
                'db.sqlite3': ['db.sqlite3'],
                '.env': ['.env']
            }
            
            for pattern, alternatives in essential_patterns.items():
                pattern_found = any(alt in content for alt in alternatives)
                self.assertTrue(pattern_found, f".gitignore에 {pattern} 또는 이와 동등한 패턴이 포함되어 있지 않습니다.")



class DockerfileTestCase(TestCase):
    """Dockerfile이 올바르게 구성되었는지 테스트합니다."""
    
    def setUp(self):
        """테스트에 필요한 파일 경로를 설정합니다."""
        self.project_root = settings.BASE_DIR
        self.dockerfile_path = os.path.join(self.project_root, 'Dockerfile')
        self.requirements_path = os.path.join(self.project_root, 'requirements.txt')
    
    def test_dockerfile_exists(self):
        """Dockerfile이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.dockerfile_path), 
                        "Dockerfile이 프로젝트 루트에 존재해야 합니다.")
    
    def test_dockerfile_content(self):
        """Dockerfile이 필요한 명령어를 포함하고 있는지 테스트합니다."""
        with open(self.dockerfile_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
        # 필수 명령어 확인
        self.assertIn('from python', content, "Dockerfile은 Python 기본 이미지를 사용해야 합니다.")
        self.assertIn('workdir', content, "Dockerfile은 작업 디렉토리를 설정해야 합니다.")
        self.assertIn('copy requirements.txt', content, "Dockerfile은 requirements.txt를 복사해야 합니다.")
        self.assertIn('run pip install', content, "Dockerfile은 의존성을 설치해야 합니다.")
        self.assertIn('copy . .', content, "Dockerfile은 애플리케이션 코드를 복사해야 합니다.")
        self.assertIn('expose', content, "Dockerfile은 포트를 노출해야 합니다.")
        self.assertIn('cmd', content, "Dockerfile은 시작 명령어를 포함해야 합니다.")
    
    def test_requirements_file_exists(self):
        """requirements.txt 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.requirements_path), 
                        "requirements.txt 파일이 프로젝트 루트에 존재해야 합니다.")


class DockerComposeTestCase(TestCase):
    """docker-compose.yml 파일이 올바르게 구성되었는지 테스트합니다."""
    
    def setUp(self):
        """테스트에 필요한 파일 경로를 설정합니다."""
        self.project_root = settings.BASE_DIR
        self.docker_compose_path = os.path.join(self.project_root, 'docker-compose.yml')
    
    def test_docker_compose_exists(self):
        """docker-compose.yml 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.docker_compose_path), 
                        "docker-compose.yml 파일이 프로젝트 루트에 존재해야 합니다.")
    
    def test_docker_compose_valid_yaml(self):
        """docker-compose.yml 파일이 유효한 YAML 형식인지 테스트합니다."""
        with open(self.docker_compose_path, 'r') as f:
            try:
                yaml_content = yaml.safe_load(f)
                self.assertIsNotNone(yaml_content, "docker-compose.yml 파일이 유효한 YAML 형식이어야 합니다.")
            except yaml.YAMLError:
                self.fail("docker-compose.yml 파일이 유효한 YAML 형식이 아닙니다.")
    
    def test_docker_compose_services(self):
        """docker-compose.yml 파일이 필요한 서비스를 포함하고 있는지 테스트합니다."""
        with open(self.docker_compose_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
            
        # 필수 서비스 확인
        self.assertIn('services', yaml_content, "docker-compose.yml 파일에 services 섹션이 있어야 합니다.")
        services = yaml_content['services']
        
        # Django 웹 서비스 확인
        self.assertIn('web', services, "docker-compose.yml 파일에 Django 웹 서비스가 정의되어 있어야 합니다.")
        web_service = services['web']
        self.assertIn('build', web_service, "웹 서비스는 build 설정을 포함해야 합니다.")
        self.assertIn('ports', web_service, "웹 서비스는 포트 매핑을 포함해야 합니다.")
        self.assertIn('depends_on', web_service, "웹 서비스는 의존성을 정의해야 합니다.")
        
        # PostgreSQL 서비스 확인
        self.assertIn('db', services, "docker-compose.yml 파일에 PostgreSQL 서비스가 정의되어 있어야 합니다.")
        db_service = services['db']
        self.assertIn('image', db_service, "DB 서비스는 이미지를 지정해야 합니다.")
        self.assertIn('volumes', db_service, "DB 서비스는 볼륨을 정의해야 합니다.")
        self.assertIn('environment', db_service, "DB 서비스는 환경 변수를 정의해야 합니다.")
        
        # Redis 서비스 확인
        self.assertIn('redis', services, "docker-compose.yml 파일에 Redis 서비스가 정의되어 있어야 합니다.")
        redis_service = services['redis']
        self.assertIn('image', redis_service, "Redis 서비스는 이미지를 지정해야 합니다.")
    
    def test_docker_compose_volumes(self):
        """docker-compose.yml 파일이 필요한 볼륨을 포함하고 있는지 테스트합니다."""
        with open(self.docker_compose_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
            
        # 볼륨 확인
        self.assertIn('volumes', yaml_content, "docker-compose.yml 파일에 볼륨 정의가 있어야 합니다.")


class DockerEnvironmentTestCase(TestCase):
    """Docker 환경 변수 설정이 올바르게 구성되었는지 테스트합니다."""
    
    def setUp(self):
        """테스트에 필요한 파일 경로를 설정합니다."""
        self.project_root = settings.BASE_DIR
        self.env_example_path = os.path.join(self.project_root, '.env.example')
        
    def test_env_example_exists(self):
        """환경 변수 예제 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.env_example_path), 
                        ".env.example 파일이 프로젝트 루트에 존재해야 합니다.")
    
    def test_env_example_content(self):
        """환경 변수 예제 파일이 필요한 변수를 포함하고 있는지 테스트합니다."""
        with open(self.env_example_path, 'r') as f:
            content = f.read()
            
        # 필수 환경 변수 확인
        self.assertIn('POSTGRES_DB', content, ".env.example 파일에 POSTGRES_DB 변수가 있어야 합니다.")
        self.assertIn('POSTGRES_USER', content, ".env.example 파일에 POSTGRES_USER 변수가 있어야 합니다.")
        self.assertIn('POSTGRES_PASSWORD', content, ".env.example 파일에 POSTGRES_PASSWORD 변수가 있어야 합니다.")
        self.assertIn('DATABASE_URL', content, ".env.example 파일에 DATABASE_URL 변수가 있어야 합니다.")
        self.assertIn('DJANGO_SECRET_KEY', content, ".env.example 파일에 DJANGO_SECRET_KEY 변수가 있어야 합니다.")
        self.assertIn('DJANGO_DEBUG', content, ".env.example 파일에 DJANGO_DEBUG 변수가 있어야 합니다.")


class DockerIntegrationTestCase(unittest.TestCase):
    """Docker 통합 테스트를 수행합니다."""
    
    @unittest.skip("실제 Docker 빌드 및 실행은 CI/CD 환경에서 수행합니다.")
    def test_docker_build(self):
        """Docker 이미지를 빌드할 수 있는지 테스트합니다."""
        client = docker.from_env()
        image, logs = client.images.build(
            path=settings.BASE_DIR,
            tag="antman:test",
            rm=True
        )
        self.assertIsNotNone(image, "Docker 이미지 빌드에 실패했습니다.")
    
    @unittest.skip("실제 Docker 실행은 CI/CD 환경에서 수행합니다.")
    def test_docker_compose_up(self):
        """docker-compose로 서비스를 시작할 수 있는지 테스트합니다."""
        import subprocess
        result = subprocess.run(
            ["docker-compose", "up", "-d"], 
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, "docker-compose up 명령 실행에 실패했습니다.")
        
        # 테스트 후 컨테이너 종료
        subprocess.run(
            ["docker-compose", "down"], 
            cwd=settings.BASE_DIR,
            capture_output=True
        )

