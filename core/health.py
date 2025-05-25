"""
Health check views for Antman project
"""
import json
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis


def health_check(request):
    """
    Health check endpoint for load balancer and monitoring
    """
    health_status = {
        "status": "healthy",
        "timestamp": request.META.get('HTTP_DATE', ''),
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "checks": {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis/Cache check
    try:
        cache.set("health_check", "ok", 30)
        cache_value = cache.get("health_check")
        if cache_value == "ok":
            health_status["checks"]["cache"] = "healthy"
        else:
            health_status["checks"]["cache"] = "unhealthy: cache test failed"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["cache"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Readiness check for Kubernetes/container orchestration
    """
    return JsonResponse({"status": "ready"})


def liveness_check(request):
    """
    Liveness check for Kubernetes/container orchestration
    """
    return JsonResponse({"status": "alive"})
