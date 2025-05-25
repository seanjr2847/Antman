#!/usr/bin/env python
"""
관계형 필드 생성 디버깅 스크립트
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

# 관계형 필드 테스트
try:
    from core.code_generation.generators import ModelGenerator
    
    generator = ModelGenerator()
    
    model_config = {
        'name': 'Order',
        'app_name': 'orders',
        'fields': [
            {'name': 'customer', 'type': 'ForeignKey', 'to': 'auth.User', 'on_delete': 'CASCADE'},
            {'name': 'product', 'type': 'ForeignKey', 'to': 'inventory.Product', 'on_delete': 'CASCADE'},
            {'name': 'quantity', 'type': 'PositiveIntegerField', 'default': 1}
        ]
    }
    
    result = generator.generate(model_config)
    print("생성된 코드:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    # 특정 패턴 확인
    if "to='auth.User'" in result:
        print("✅ to='auth.User' 패턴 발견")
    else:
        print("❌ to='auth.User' 패턴 없음")
        
    if "'auth.User'" in result:
        print("✅ 'auth.User' 패턴 발견")
    else:
        print("❌ 'auth.User' 패턴 없음")
    
except Exception as e:
    print(f"❌ 모델 생성 실패: {e}")
    import traceback
    traceback.print_exc()
