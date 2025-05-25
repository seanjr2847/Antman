import os
import unittest
import yaml
from django.test import TestCase
from django.conf import settings


class NginxConfigTestCase(TestCase):
    """Nginx 설정 파일이 올바르게 구성되었는지 테스트합니다."""
    
    def setUp(self):
        """테스트에 필요한 파일 경로를 설정합니다."""
        self.project_root = settings.BASE_DIR
        self.nginx_conf_path = os.path.join(self.project_root, 'nginx', 'nginx.conf')
        self.nginx_default_conf_path = os.path.join(self.project_root, 'nginx', 'default.conf')
        self.docker_compose_path = os.path.join(self.project_root, 'docker-compose.yml')
    
    def test_nginx_directory_exists(self):
        """Nginx 설정 디렉토리가 존재하는지 테스트합니다."""
        nginx_dir = os.path.join(self.project_root, 'nginx')
        self.assertTrue(os.path.exists(nginx_dir), 
                       "Nginx 설정 디렉토리가 프로젝트 루트에 존재해야 합니다.")
    
    def test_nginx_conf_exists(self):
        """nginx.conf 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.nginx_conf_path), 
                       "nginx.conf 파일이 nginx 디렉토리에 존재해야 합니다.")
    
    def test_nginx_default_conf_exists(self):
        """default.conf 파일이 존재하는지 테스트합니다."""
        self.assertTrue(os.path.exists(self.nginx_default_conf_path), 
                       "default.conf 파일이 nginx 디렉토리에 존재해야 합니다.")
    
    def test_nginx_conf_content(self):
        """nginx.conf 파일이 필요한 설정을 포함하고 있는지 테스트합니다."""
        with open(self.nginx_conf_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
        # 필수 설정 확인
        self.assertIn('worker_processes', content, "nginx.conf 파일에 worker_processes 설정이 있어야 합니다.")
        self.assertIn('events', content, "nginx.conf 파일에 events 섹션이 있어야 합니다.")
        self.assertIn('http', content, "nginx.conf 파일에 http 섹션이 있어야 합니다.")
        self.assertIn('include', content, "nginx.conf 파일에 include 지시자가 있어야 합니다.")
        self.assertIn('gzip', content, "nginx.conf 파일에 gzip 설정이 있어야 합니다.")
    
    def test_nginx_default_conf_content(self):
        """default.conf 파일이 필요한 설정을 포함하고 있는지 테스트합니다."""
        with open(self.nginx_default_conf_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
        # 필수 설정 확인
        self.assertIn('server', content, "default.conf 파일에 server 블록이 있어야 합니다.")
        self.assertIn('listen', content, "default.conf 파일에 listen 지시자가 있어야 합니다.")
        self.assertIn('location', content, "default.conf 파일에 location 블록이 있어야 합니다.")
        self.assertIn('proxy_pass', content, "default.conf 파일에 proxy_pass 지시자가 있어야 합니다.")
        self.assertIn('static', content, "default.conf 파일에 static 파일 설정이 있어야 합니다.")
        self.assertIn('media', content, "default.conf 파일에 media 파일 설정이 있어야 합니다.")
        
        # 캐싱 및 헤더 설정 확인
        self.assertIn('proxy_set_header', content, "default.conf 파일에 proxy_set_header 지시자가 있어야 합니다.")
        self.assertIn('expires', content, "default.conf 파일에 expires 설정이 있어야 합니다.")
    
    def test_docker_compose_nginx_service(self):
        """docker-compose.yml 파일에 Nginx 서비스가 구성되어 있는지 테스트합니다."""
        with open(self.docker_compose_path, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)
            
        # Nginx 서비스 확인
        self.assertIn('services', yaml_content, "docker-compose.yml 파일에 services 섹션이 있어야 합니다.")
        services = yaml_content['services']
        
        self.assertIn('nginx', services, "docker-compose.yml 파일에 nginx 서비스가 정의되어 있어야 합니다.")
        nginx_service = services['nginx']
        
        # Nginx 서비스 구성 확인
        self.assertIn('image', nginx_service, "nginx 서비스에 이미지가 지정되어 있어야 합니다.")
        self.assertIn('ports', nginx_service, "nginx 서비스에 포트 매핑이 정의되어 있어야 합니다.")
        self.assertIn('volumes', nginx_service, "nginx 서비스에 볼륨이 정의되어 있어야 합니다.")
        self.assertIn('depends_on', nginx_service, "nginx 서비스에 의존성이 정의되어 있어야 합니다.")
        
        # 포트 확인
        ports = nginx_service['ports']
        has_port_80 = any('80:' in port for port in ports) if isinstance(ports, list) else '80:' in ports
        self.assertTrue(has_port_80, "nginx 서비스는 80 포트를 노출해야 합니다.")
        
        # 볼륨 확인
        volumes = nginx_service['volumes']
        has_nginx_conf = any('nginx.conf' in volume for volume in volumes) if isinstance(volumes, list) else 'nginx.conf' in volumes
        self.assertTrue(has_nginx_conf, "nginx 서비스에 nginx.conf 파일이 마운트되어 있어야 합니다.")
        
        # 의존성 확인
        self.assertIn('web', nginx_service['depends_on'], "nginx 서비스는 web 서비스에 의존해야 합니다.")


class NginxIntegrationTestCase(unittest.TestCase):
    """Nginx 통합 테스트를 수행합니다."""
    
    @unittest.skip("실제 Nginx 구성 테스트는 CI/CD 환경에서 수행합니다.")
    def test_nginx_static_file_serving(self):
        """Nginx가 정적 파일을 올바르게 제공하는지 테스트합니다."""
        import requests
        
        # 로컬 Nginx 서버에 요청
        response = requests.get('http://localhost/static/css/style.css')
        self.assertEqual(response.status_code, 200, "Nginx는 정적 파일에 대한 요청에 200 상태 코드를 반환해야 합니다.")
        
        # 캐싱 헤더 확인
        self.assertIn('Cache-Control', response.headers, "Nginx는 정적 파일에 대한 캐싱 헤더를 설정해야 합니다.")
    
    @unittest.skip("실제 Nginx 구성 테스트는 CI/CD 환경에서 수행합니다.")
    def test_nginx_proxy_to_django(self):
        """Nginx가 요청을 Django 애플리케이션으로 올바르게 프록시하는지 테스트합니다."""
        import requests
        
        # 로컬 Nginx 서버에 요청
        response = requests.get('http://localhost/')
        self.assertEqual(response.status_code, 200, "Nginx는 Django 애플리케이션으로 요청을 프록시해야 합니다.")
        
        # Django 응답 확인
        self.assertIn('Django', response.text, "응답은 Django 애플리케이션에서 생성되어야 합니다.")
