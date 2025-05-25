#!/usr/bin/env python
"""
미들웨어 테스트 디버깅 스크립트
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

# 미들웨어 테스트
try:
    from unittest.mock import MagicMock
    from django.test import RequestFactory
    from django.http import HttpResponse
    
    from core.error_handling.middleware import (
        ErrorHandlingMiddleware,
        APIErrorHandlingMiddleware,
        RequestLoggingErrorMiddleware
    )
    
    print("미들웨어 클래스 가져오기 성공")
    
    # RequestFactory 생성
    factory = RequestFactory()
    get_response = MagicMock(return_value=HttpResponse())
    
    # 각 미들웨어 초기화 테스트
    try:
        middleware1 = ErrorHandlingMiddleware(get_response=get_response)
        print("✅ ErrorHandlingMiddleware 초기화 성공")
    except Exception as e:
        print(f"❌ ErrorHandlingMiddleware 초기화 실패: {e}")
    
    try:
        middleware2 = APIErrorHandlingMiddleware(get_response=get_response)
        print("✅ APIErrorHandlingMiddleware 초기화 성공")
    except Exception as e:
        print(f"❌ APIErrorHandlingMiddleware 초기화 실패: {e}")
    
    try:
        middleware3 = RequestLoggingErrorMiddleware(get_response=get_response)
        print("✅ RequestLoggingErrorMiddleware 초기화 성공")
    except Exception as e:
        print(f"❌ RequestLoggingErrorMiddleware 초기화 실패: {e}")
    
    # 미들웨어 호출 테스트
    request = factory.get('/api/test/')
    
    try:
        response = middleware1(request)
        print("✅ ErrorHandlingMiddleware 호출 성공")
    except Exception as e:
        print(f"❌ ErrorHandlingMiddleware 호출 실패: {e}")
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
