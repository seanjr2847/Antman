"""
URL configuration for antman project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# 헬스 체크 뷰 함수
def health_check(request):
    """헬스 체크 엔드포인트
    
    시스템의 상태를 확인하는 간단한 헬스 체크 엔드포인트입니다.
    """
    return JsonResponse({'status': 'ok'})

# 홈페이지 뷰 함수
def home(request):
    """홈페이지 엔드포인트
    
    Antman 프로젝트의 기본 홈페이지를 제공합니다.
    """
    return JsonResponse({
        'message': 'Antman 프로젝트에 오신 것을 환영합니다',
        'version': '1.0.0',
        'status': 'running'
    })

urlpatterns = [
    path('', home, name='home'),  # 홈페이지 URL 추가
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
]
