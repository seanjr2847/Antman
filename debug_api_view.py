#!/usr/bin/env python
"""
API 뷰 생성 디버깅 스크립트
"""
import os
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antman.test_settings')

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import django
    django.setup()
    print("✅ Django 설정 성공")
except Exception as e:
    print(f"❌ Django 설정 실패: {e}")
    sys.exit(1)

# API 뷰 테스트
try:
    from core.code_generation.generators import ViewGenerator
    
    generator = ViewGenerator()
    
    view_config = {
        'name': 'ProductAPIView',
        'type': 'APIView',
        'model': 'Product',
        'app_name': 'inventory',
        'methods': ['GET', 'POST']
    }
    
    result = generator.generate(view_config)
    print("생성된 코드:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    # 특정 패턴 확인
    if "def get(self, request):" in result:
        print("✅ def get(self, request): 패턴 발견")
    else:
        print("❌ def get(self, request): 패턴 없음")
        
    if "def get(self, request, pk=None):" in result:
        print("✅ def get(self, request, pk=None): 패턴 발견")
    else:
        print("❌ def get(self, request, pk=None): 패턴 없음")
    
except Exception as e:
    print(f"❌ 뷰 생성 실패: {e}")
    import traceback
    traceback.print_exc()
