"""
시스템 통합 테스트 모듈.

이 모듈은 Antman 시스템의 전체 통합 테스트를 포함합니다.
모든 주요 컴포넌트가 함께 작동하는지 확인하고 
문서화 및 핵심 기능을 검증합니다.
"""

import os
import re
import json
import time
import importlib
import unittest
from unittest import mock
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.apps import apps

# 핵심 기능 모듈 가져오기
from core.error_handling.base import AntmanBaseException
from core.code_generation.base import BaseGenerator


class SystemIntegrationTestCase(TestCase):
    """시스템 통합 테스트 케이스"""
    
    def setUp(self):
        """테스트 설정"""
        self.client = Client()
    
    def test_all_apps_installed(self):
        """모든 필수 앱이 올바르게 설치되었는지 확인"""
        required_apps = [
            'apps', 'core', 'core.error_handling', 'core.code_generation', 
            'core.middleware', 'core.code_quality'
        ]
        
        for app_name in required_apps:
            try:
                app_config = apps.get_app_config(app_name.split('.')[-1])
                self.assertIsNotNone(app_config, f"{app_name} 앱이 설치되지 않았습니다")
            except LookupError:
                self.fail(f"{app_name} 앱을 찾을 수 없습니다")
    
    def test_health_check_endpoint(self):
        """헬스 체크 엔드포인트가 올바르게 작동하는지 확인"""
        # 실제 URL 경로는 프로젝트 설정에 따라 다를 수 있음
        try:
            response = self.client.get('/health/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('status', response.json())
            self.assertEqual(response.json()['status'], 'ok')
        except Exception as e:
            self.fail(f"헬스 체크 엔드포인트가 올바르게 작동하지 않습니다: {str(e)}")
    
    def test_core_modules_integration(self):
        """핵심 모듈 통합이 올바르게 작동하는지 확인"""
        # 에러 처리 모듈 테스트
        try:
            error = AntmanBaseException("테스트 에러")
            self.assertEqual(str(error), "테스트 에러")
        except ImportError:
            self.fail("에러 처리 모듈을 가져올 수 없습니다")
        
        # 코드 생성 모듈 테스트
        try:
            # BaseGenerator는 추상 클래스이므로 구체적인 구현체 생성 대신 import 확인
            self.assertTrue(hasattr(BaseGenerator, 'generate'))
            self.assertTrue(hasattr(BaseGenerator, '_validate_config'))
            self.assertTrue(hasattr(BaseGenerator, 'save'))
        except ImportError:
            self.fail("코드 생성 모듈을 가져올 수 없습니다")


class DocumentationTestCase(TestCase):
    """문서화 테스트 케이스"""
    
    def test_readme_exists(self):
        """README 파일이 존재하는지 확인"""
        readme_path = os.path.join(settings.BASE_DIR, 'README.md')
        self.assertTrue(os.path.exists(readme_path), "README.md 파일이 존재하지 않습니다")
        
        # README 내용 검증
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 필수 섹션 확인
        required_sections = ['설치', '사용법', '구성', '개발']
        for section in required_sections:
            # # 설치, ## 설치, ### 설치 와 같은 형태를 찾는 정규표현식
            pattern = rf'#\s*{section}|#{2}\s*{section}|#{3}\s*{section}'
            self.assertTrue(re.search(pattern, content, re.IGNORECASE), 
                          f"README에 '{section}' 섹션이 없습니다")
    
    def test_api_documentation(self):
        """API 문서가 존재하는지 확인"""
        docs_path = os.path.join(settings.BASE_DIR, 'docs')
        api_docs_path = os.path.join(docs_path, 'api')
        
        self.assertTrue(os.path.exists(docs_path), "docs 디렉토리가 존재하지 않습니다")
        self.assertTrue(os.path.exists(api_docs_path), "API 문서 디렉토리가 존재하지 않습니다")
        
        # 최소한 하나의 API 문서 파일이 있어야 함
        api_doc_files = [f for f in os.listdir(api_docs_path) 
                         if f.endswith('.md') or f.endswith('.rst')]
        self.assertTrue(len(api_doc_files) > 0, "API 문서 파일이 없습니다")
    
    def test_code_comments(self):
        """주요 코드 파일에 적절한 주석이 있는지 확인"""
        core_paths = [
            os.path.join(settings.BASE_DIR, 'core', 'code_generation'),
            os.path.join(settings.BASE_DIR, 'core', 'error_handling'),
            os.path.join(settings.BASE_DIR, 'core', 'middleware')
        ]
        
        for path in core_paths:
            self.assertTrue(os.path.exists(path), f"{path} 경로가 존재하지 않습니다")
            
            py_files = [f for f in os.listdir(path) if f.endswith('.py')]
            self.assertTrue(len(py_files) > 0, f"{path}에 Python 파일이 없습니다")
            
            # 각 파일에 docstring이 있는지 확인
            for py_file in py_files:
                file_path = os.path.join(path, py_file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 문서 문자열 확인
                self.assertTrue('"""' in content or "'''" in content, 
                              f"{file_path}에 문서 문자열이 없습니다")


class DeploymentTestCase(TestCase):
    """배포 설정 테스트 케이스"""
    
    def test_docker_compose_files(self):
        """Docker Compose 파일이 올바르게 구성되었는지 확인"""
        compose_files = [
            os.path.join(settings.BASE_DIR, 'docker-compose.yml'),
            os.path.join(settings.BASE_DIR, 'docker-compose.staging.yml'),
            os.path.join(settings.BASE_DIR, 'docker-compose.production.yml')
        ]
        
        for file_path in compose_files:
            self.assertTrue(os.path.exists(file_path), 
                          f"{os.path.basename(file_path)}이 존재하지 않습니다")
    
    def test_ci_cd_configuration(self):
        """CI/CD 설정이 올바르게 구성되었는지 확인"""
        gitlab_ci_path = os.path.join(settings.BASE_DIR, '.gitlab-ci.yml')
        self.assertTrue(os.path.exists(gitlab_ci_path), ".gitlab-ci.yml 파일이 존재하지 않습니다")
        
        # CI/CD 파일 내용 검증
        with open(gitlab_ci_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 단계 확인
        required_stages = ['lint', 'test', 'build', 'security', 'deploy']
        for stage in required_stages:
            self.assertIn(stage, content, f"CI/CD 설정에 '{stage}' 단계가 없습니다")
    
    def test_deployment_scripts(self):
        """배포 스크립트가 존재하는지 확인"""
        scripts_path = os.path.join(settings.BASE_DIR, 'scripts')
        self.assertTrue(os.path.exists(scripts_path), "scripts 디렉토리가 존재하지 않습니다")
        
        required_scripts = ['deploy.sh', 'rollback.sh', 'backup.sh']
        for script in required_scripts:
            script_path = os.path.join(scripts_path, script)
            self.assertTrue(os.path.exists(script_path), f"{script} 스크립트가 존재하지 않습니다")
            
            # 스크립트 실행 권한 확인
            self.assertTrue(os.access(script_path, os.X_OK), 
                          f"{script} 스크립트에 실행 권한이 없습니다")


class PerformanceTestCase(TestCase):
    """성능 테스트 케이스"""
    
    @pytest.mark.skip(reason="성능 테스트는 CI/CD 환경에서만 실행됩니다")
    def test_load_performance(self):
        """기본 로드 성능 테스트"""
        # 실제 환경에서는 더 복잡한 성능 테스트를 수행해야 함
        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        # 응답 시간이 500ms 미만인지 확인
        self.assertLess(end_time - start_time, 0.5, 
                      "홈 페이지 로드 시간이 500ms를 초과합니다")


if __name__ == '__main__':
    unittest.main()
