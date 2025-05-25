import os
import sys
import unittest
import importlib
from pathlib import Path
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from io import StringIO


class TestFrameworkTestCase(TestCase):
    """테스트 프레임워크가 올바르게 구성되었는지 테스트합니다."""
    
    def setUp(self):
        """테스트에 필요한 설정을 합니다."""
        self.project_root = settings.BASE_DIR
        self.test_settings_path = os.path.join(self.project_root, 'antman', 'test_settings.py')
        self.pytest_conf_path = os.path.join(self.project_root, 'pytest.ini')
        self.coverage_conf_path = os.path.join(self.project_root, '.coveragerc')
        self.conftest_path = os.path.join(self.project_root, 'conftest.py')
    
    def test_test_settings_exists(self):
        """테스트를 위한 설정 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.test_settings_path), 
                        "테스트 설정 파일이 존재해야 합니다.")
    
    def test_pytest_conf_exists(self):
        """pytest.ini 설정 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.pytest_conf_path), 
                        "pytest.ini 파일이 존재해야 합니다.")
    
    def test_coverage_conf_exists(self):
        """.coveragerc 설정 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.coverage_conf_path), 
                        ".coveragerc 파일이 존재해야 합니다.")
    
    def test_conftest_exists(self):
        """conftest.py 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.conftest_path), 
                        "conftest.py 파일이 존재해야 합니다.")
    
    def test_test_settings_content(self):
        """테스트 설정 파일이 올바른 설정을 포함하고 있는지 테스트합니다."""
        with open(self.test_settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 설정 확인
        self.assertIn('DEBUG = True', content, "테스트 설정 파일에 DEBUG = True가 포함되어야 합니다.")
        self.assertIn('DATABASES', content, "테스트 설정 파일에 DATABASES 설정이 포함되어야 합니다.")
        self.assertIn('sqlite3', content.lower(), "테스트 설정 파일은 테스트용 SQLite 데이터베이스를 사용해야 합니다.")
    
    def test_pytest_conf_content(self):
        """pytest.ini 파일이 올바른 설정을 포함하고 있는지 테스트합니다."""
        with open(self.pytest_conf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 설정 확인
        self.assertIn('DJANGO_SETTINGS_MODULE', content, "pytest.ini 파일에 DJANGO_SETTINGS_MODULE 설정이 포함되어야 합니다.")
        self.assertIn('python_files', content, "pytest.ini 파일에 python_files 설정이 포함되어야 합니다.")
    
    def test_coverage_conf_content(self):
        """.coveragerc 파일이 올바른 설정을 포함하고 있는지 테스트합니다."""
        with open(self.coverage_conf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 설정 확인
        self.assertIn('[run]', content, ".coveragerc 파일에 [run] 섹션이 포함되어야 합니다.")
        self.assertIn('source', content, ".coveragerc 파일에 source 설정이 포함되어야 합니다.")
        self.assertIn('omit', content, ".coveragerc 파일에 omit 설정이 포함되어야 합니다.")
    
    def test_factory_boy_installed(self):
        """factory-boy 패키지가 설치되어 있는지 테스트합니다."""
        try:
            import factory
            self.assertTrue(True, "factory-boy 패키지가 설치되어 있습니다.")
        except ImportError:
            self.fail("factory-boy 패키지가 설치되어 있지 않습니다.")
    
    def test_pytest_django_installed(self):
        """pytest-django 패키지가 설치되어 있는지 테스트합니다."""
        try:
            import pytest_django
            self.assertTrue(True, "pytest-django 패키지가 설치되어 있습니다.")
        except ImportError:
            self.fail("pytest-django 패키지가 설치되어 있지 않습니다.")
    
    def test_coverage_installed(self):
        """coverage 패키지가 설치되어 있는지 테스트합니다."""
        try:
            import coverage
            self.assertTrue(True, "coverage 패키지가 설치되어 있습니다.")
        except ImportError:
            self.fail("coverage 패키지가 설치되어 있지 않습니다.")


class ModelTestCaseExample(TestCase):
    """Django 모델 테스트 케이스 예제가 올바르게 구성되었는지 테스트합니다."""
    
    def test_model_test_exists(self):
        """최소한 하나의 모델 테스트 클래스가 존재하는지 테스트합니다."""
        # 현재 존재하는 앱 확인
        apps_dir = os.path.join(settings.BASE_DIR, 'apps')
        app_names = [name for name in os.listdir(apps_dir) 
                    if os.path.isdir(os.path.join(apps_dir, name)) and name != '__pycache__']
        
        model_tests_found = False
        for app_name in app_names:
            tests_file = os.path.join(apps_dir, app_name, 'tests.py')
            test_dir = os.path.join(apps_dir, app_name, 'tests')
            
            # tests.py 파일 확인
            if os.path.exists(tests_file):
                with open(tests_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'class' in content and 'Model' in content and 'Test' in content:
                        model_tests_found = True
                        break
            
            # tests 디렉토리 확인
            if os.path.exists(test_dir) and os.path.isdir(test_dir):
                for test_file in os.listdir(test_dir):
                    if test_file.endswith('.py') and test_file != '__init__.py':
                        with open(os.path.join(test_dir, test_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'class' in content and 'Model' in content and 'Test' in content:
                                model_tests_found = True
                                break
            
            if model_tests_found:
                break
        
        self.assertTrue(model_tests_found, "최소한 하나의 모델 테스트 클래스가 존재해야 합니다.")


class ViewTestCaseExample(TestCase):
    """Django 뷰 테스트 케이스 예제가 올바르게 구성되었는지 테스트합니다."""
    
    def test_view_test_exists(self):
        """최소한 하나의 뷰 테스트 클래스가 존재하는지 테스트합니다."""
        # 현재 존재하는 앱 확인
        apps_dir = os.path.join(settings.BASE_DIR, 'apps')
        app_names = [name for name in os.listdir(apps_dir) 
                    if os.path.isdir(os.path.join(apps_dir, name)) and name != '__pycache__']
        
        view_tests_found = False
        for app_name in app_names:
            tests_file = os.path.join(apps_dir, app_name, 'tests.py')
            test_dir = os.path.join(apps_dir, app_name, 'tests')
            
            # tests.py 파일 확인
            if os.path.exists(tests_file):
                with open(tests_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'class' in content and 'View' in content and 'Test' in content:
                        view_tests_found = True
                        break
            
            # tests 디렉토리 확인
            if os.path.exists(test_dir) and os.path.isdir(test_dir):
                for test_file in os.listdir(test_dir):
                    if test_file.endswith('.py') and test_file != '__init__.py':
                        with open(os.path.join(test_dir, test_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'class' in content and 'View' in content and 'Test' in content:
                                view_tests_found = True
                                break
            
            if view_tests_found:
                break
        
        self.assertTrue(view_tests_found, "최소한 하나의 뷰 테스트 클래스가 존재해야 합니다.")


class TestFixtureTestCase(TestCase):
    """테스트 픽스처가 올바르게 구성되었는지 테스트합니다."""
    
    def test_fixture_directory_exists(self):
        """테스트 픽스처 디렉토리가 존재하는지 테스트합니다."""
        fixture_dir = os.path.join(settings.BASE_DIR, 'fixtures')
        self.assertTrue(os.path.exists(fixture_dir) and os.path.isdir(fixture_dir), 
                        "테스트 픽스처 디렉토리가 존재해야 합니다.")
    
    def test_factory_classes_exist(self):
        """Factory 클래스가 존재하는지 테스트합니다."""
        # 현재 존재하는 앱 확인
        apps_dir = os.path.join(settings.BASE_DIR, 'apps')
        app_names = [name for name in os.listdir(apps_dir) 
                    if os.path.isdir(os.path.join(apps_dir, name)) and name != '__pycache__']
        
        factory_found = False
        for app_name in app_names:
            factories_file = os.path.join(apps_dir, app_name, 'factories.py')
            
            if os.path.exists(factories_file):
                with open(factories_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'class' in content and 'Factory' in content:
                        factory_found = True
                        break
        
        self.assertTrue(factory_found, "최소한 하나의 Factory 클래스가 존재해야 합니다.")


class TestRunnerTestCase(unittest.TestCase):
    """테스트 실행기가 올바르게 작동하는지 테스트합니다."""
    
    @unittest.skip("실제 테스트 실행은 CI/CD 환경에서 수행합니다.")
    def test_django_test_command(self):
        """Django 테스트 명령이 오류 없이 실행되는지 테스트합니다."""
        output = StringIO()
        call_command('test', 'core.test_framework_tests.TestFrameworkTestCase.test_test_settings_exists', stdout=output)
        self.assertNotIn('Error', output.getvalue(), "Django 테스트 명령이 오류 없이 실행되어야 합니다.")
    
    @unittest.skip("실제 테스트 실행은 CI/CD 환경에서 수행합니다.")
    def test_pytest_command(self):
        """pytest 명령이 오류 없이 실행되는지 테스트합니다."""
        import subprocess
        
        result = subprocess.run(
            ["pytest", "core/test_framework_tests.py::TestFrameworkTestCase::test_test_settings_exists", "-v"],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, "pytest 명령이 오류 없이 실행되어야 합니다.")
    
    @unittest.skip("실제 테스트 실행은 CI/CD 환경에서 수행합니다.")
    def test_coverage_command(self):
        """coverage 명령이 오류 없이 실행되는지 테스트합니다."""
        import subprocess
        
        result = subprocess.run(
            ["coverage", "run", "manage.py", "test", "core.test_framework_tests.TestFrameworkTestCase.test_test_settings_exists"],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, "coverage 명령이 오류 없이 실행되어야 합니다.")
