"""
GitLab CI/CD 파이프라인 테스트
"""
import os
import sys
import pytest
import yaml
from pathlib import Path

# Django 설정을 위한 환경 변수 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.test')

# Django 앱 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestGitLabCIPipeline:
    """GitLab CI/CD 파이프라인 설정 테스트"""
    
    @pytest.fixture
    def ci_config_path(self):
        """CI 설정 파일 경로"""
        return Path(".gitlab-ci.yml")
    
    @pytest.fixture
    def ci_config(self, ci_config_path):
        """CI 설정 로드"""
        if ci_config_path.exists():
            with open(ci_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return None
    
    def test_gitlab_ci_file_exists(self, ci_config_path):
        """GitLab CI 설정 파일이 존재하는지 확인"""
        assert ci_config_path.exists(), ".gitlab-ci.yml 파일이 존재해야 합니다"
    
    def test_pipeline_stages_defined(self, ci_config):
        """필수 파이프라인 단계가 정의되어 있는지 확인"""
        assert ci_config is not None, "CI 설정을 로드할 수 없습니다"
        assert 'stages' in ci_config, "stages가 정의되어야 합니다"
        
        required_stages = ['lint', 'test', 'build', 'security', 'deploy']
        for stage in required_stages:
            assert stage in ci_config['stages'], f"{stage} 단계가 필요합니다"
    
    def test_lint_job_configuration(self, ci_config):
        """Linting 작업 설정 확인"""
        assert 'lint' in ci_config, "lint 작업이 정의되어야 합니다"
        lint_job = ci_config['lint']
        
        assert lint_job['stage'] == 'lint', "lint 작업은 lint 단계에 있어야 합니다"
        assert 'script' in lint_job, "lint 스크립트가 정의되어야 합니다"
        
        # flake8과 black 체크 확인
        scripts = ' '.join(lint_job['script'])
        assert 'flake8' in scripts or 'ruff' in scripts, "Python linting 도구가 필요합니다"
        assert 'black' in scripts or 'isort' in scripts, "코드 포매팅 도구가 필요합니다"
    
    def test_test_job_configuration(self, ci_config):
        """테스트 작업 설정 확인"""
        assert 'test' in ci_config, "test 작업이 정의되어야 합니다"
        test_job = ci_config['test']
        
        assert test_job['stage'] == 'test', "test 작업은 test 단계에 있어야 합니다"
        assert 'script' in test_job, "test 스크립트가 정의되어야 합니다"
        assert 'coverage' in test_job, "coverage 설정이 필요합니다"
        
        # pytest 실행 확인
        scripts = ' '.join(test_job['script'])
        assert 'pytest' in scripts, "pytest 실행이 필요합니다"
        assert '--cov' in scripts, "코드 커버리지 측정이 필요합니다"
        
        # 아티팩트 설정 확인
        assert 'artifacts' in test_job, "테스트 아티팩트 설정이 필요합니다"
        assert 'reports' in test_job['artifacts'], "테스트 리포트 설정이 필요합니다"
    
    def test_docker_build_job_configuration(self, ci_config):
        """Docker 빌드 작업 설정 확인"""
        assert 'build-docker' in ci_config, "Docker 빌드 작업이 정의되어야 합니다"
        build_job = ci_config['build-docker']
        
        assert build_job['stage'] == 'build', "Docker 빌드는 build 단계에 있어야 합니다"
        assert 'image' in build_job, "Docker 이미지가 지정되어야 합니다"
        assert 'services' in build_job, "Docker 서비스가 필요합니다"
        assert 'docker:dind' in build_job['services'], "Docker-in-Docker 서비스가 필요합니다"
        
        # Docker 빌드 및 푸시 확인
        scripts = ' '.join(build_job['script'])
        assert 'docker build' in scripts, "Docker 빌드 명령이 필요합니다"
        assert 'docker push' in scripts, "Docker 푸시 명령이 필요합니다"
    
    def test_security_scanning_configuration(self, ci_config):
        """보안 스캔 작업 설정 확인"""
        # 의존성 스캔
        assert 'dependency-scan' in ci_config, "의존성 스캔 작업이 필요합니다"
        dep_scan = ci_config['dependency-scan']
        assert dep_scan['stage'] == 'security', "의존성 스캔은 security 단계에 있어야 합니다"
        
        # Docker 이미지 스캔
        assert 'container-scan' in ci_config, "컨테이너 스캔 작업이 필요합니다"
        container_scan = ci_config['container-scan']
        assert container_scan['stage'] == 'security', "컨테이너 스캔은 security 단계에 있어야 합니다"
    
    def test_deployment_configuration(self, ci_config):
        """배포 설정 확인"""
        # Staging 배포
        assert 'deploy-staging' in ci_config, "Staging 배포 작업이 필요합니다"
        staging_job = ci_config['deploy-staging']
        assert staging_job['stage'] == 'deploy', "Staging 배포는 deploy 단계에 있어야 합니다"
        assert 'environment' in staging_job, "Staging 환경 설정이 필요합니다"
        assert staging_job['environment']['name'] == 'staging', "Staging 환경 이름이 설정되어야 합니다"
        
        # Production 배포
        assert 'deploy-production' in ci_config, "Production 배포 작업이 필요합니다"
        prod_job = ci_config['deploy-production']
        assert prod_job['stage'] == 'deploy', "Production 배포는 deploy 단계에 있어야 합니다"
        assert 'when' in prod_job and prod_job['when'] == 'manual', "Production 배포는 수동 승인이 필요합니다"
        assert 'environment' in prod_job, "Production 환경 설정이 필요합니다"
        assert prod_job['environment']['name'] == 'production', "Production 환경 이름이 설정되어야 합니다"
    
    def test_rollback_mechanism(self, ci_config):
        """롤백 메커니즘 확인"""
        assert 'rollback-staging' in ci_config, "Staging 롤백 작업이 필요합니다"
        assert 'rollback-production' in ci_config, "Production 롤백 작업이 필요합니다"
        
        # 롤백 작업은 수동 실행
        rollback_staging = ci_config['rollback-staging']
        rollback_prod = ci_config['rollback-production']
        
        assert rollback_staging['when'] == 'manual', "Staging 롤백은 수동 실행이어야 합니다"
        assert rollback_prod['when'] == 'manual', "Production 롤백은 수동 실행이어야 합니다"
    
    def test_variables_and_secrets(self, ci_config):
        """환경 변수 및 시크릿 설정 확인"""
        assert 'variables' in ci_config, "전역 변수 설정이 필요합니다"
        
        # Docker 레지스트리 설정
        variables = ci_config['variables']
        assert 'DOCKER_REGISTRY' in variables or 'CI_REGISTRY' in variables, "Docker 레지스트리 설정이 필요합니다"
    
    def test_cache_configuration(self, ci_config):
        """캐시 설정 확인"""
        # 최소 하나의 작업에 캐시가 설정되어 있는지 확인
        cache_found = False
        for job_name, job_config in ci_config.items():
            if isinstance(job_config, dict) and 'cache' in job_config:
                cache_found = True
                break
        
        assert cache_found, "파이프라인 성능을 위해 캐시 설정이 필요합니다"
    
    def test_notification_configuration(self, ci_config):
        """알림 설정 확인"""
        # 실패 알림이 설정되어 있는지 확인
        notification_found = False
        for job_name, job_config in ci_config.items():
            if isinstance(job_config, dict):
                if 'after_script' in job_config:
                    scripts = ' '.join(job_config['after_script'])
                    if 'mail' in scripts or 'email' in scripts:
                        notification_found = True
                        break
        
        assert notification_found, "파이프라인 실패 시 이메일 알림 설정이 필요합니다"


class TestDeploymentScripts:
    """배포 스크립트 테스트"""
    
    def test_deployment_script_exists(self):
        """배포 스크립트가 존재하는지 확인"""
        deploy_script = Path("scripts/deploy.sh")
        assert deploy_script.exists(), "배포 스크립트가 필요합니다"
        
        # 실행 권한 확인 (Unix 시스템에서만)
        if os.name != 'nt':  # Windows가 아닌 경우
            assert os.access(deploy_script, os.X_OK), "배포 스크립트는 실행 가능해야 합니다"
    
    def test_rollback_script_exists(self):
        """롤백 스크립트가 존재하는지 확인"""
        rollback_script = Path("scripts/rollback.sh")
        assert rollback_script.exists(), "롤백 스크립트가 필요합니다"
        
        # 실행 권한 확인 (Unix 시스템에서만)
        if os.name != 'nt':  # Windows가 아닌 경우
            assert os.access(rollback_script, os.X_OK), "롤백 스크립트는 실행 가능해야 합니다"


class TestDockerConfiguration:
    """Docker 설정 테스트"""
    
    def test_dockerfile_exists(self):
        """Dockerfile이 존재하는지 확인"""
        dockerfile = Path("Dockerfile")
        assert dockerfile.exists(), "Dockerfile이 필요합니다"
    
    def test_dockerignore_exists(self):
        """.dockerignore 파일이 존재하는지 확인"""
        dockerignore = Path(".dockerignore")
        assert dockerignore.exists(), ".dockerignore 파일이 필요합니다"
    
    def test_docker_compose_exists(self):
        """Docker Compose 파일이 존재하는지 확인"""
        compose_files = [
            Path("docker-compose.yml"),
            Path("docker-compose.yaml"),
            Path("compose.yml"),
            Path("compose.yaml")
        ]
        
        compose_exists = any(f.exists() for f in compose_files)
        assert compose_exists, "Docker Compose 파일이 필요합니다"
