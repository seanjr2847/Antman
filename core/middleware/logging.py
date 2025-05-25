"""
Logging middleware for request/response tracking.
"""
import json
import time
import uuid
import logging
from typing import Dict, Any, Optional
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log request and response details."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response or (lambda request: None)
        self.log_body = getattr(settings, 'LOG_REQUEST_BODY', False)
        self.log_headers = getattr(settings, 'LOG_REQUEST_HEADERS', True)
        self.log_response = getattr(settings, 'LOG_RESPONSE_BODY', False)
        self.exclude_paths = getattr(settings, 'LOGGING_EXCLUDE_PATHS', [
            '/health/',
            '/metrics/',
            '/admin/jsi18n/',
            '/static/',
            '/media/'
        ])
        self.sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token'
        }
    
    def process_request(self, request: HttpRequest) -> None:
        """Process incoming request."""
        # Skip logging for excluded paths
        if any(request.path.startswith(path) for path in self.exclude_paths):
            return
        
        # Generate unique request ID
        request.request_id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # Prepare log data
        log_data = {
            'request_id': request.request_id,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'content_length': request.META.get('CONTENT_LENGTH', 0)
        }
        
        # Add headers if enabled
        if self.log_headers:
            log_data['headers'] = self._sanitize_headers(request.META)
        
        # Add body if enabled and present
        if self.log_body and hasattr(request, 'body'):
            try:
                body = request.body.decode('utf-8')
                if body:
                    # Try to parse as JSON for better logging
                    try:
                        log_data['body'] = json.loads(body)
                    except json.JSONDecodeError:
                        log_data['body'] = body[:1000]  # Limit body size
            except Exception:
                log_data['body'] = '<Unable to decode body>'
        
        logger.info(f"Request started: {request.method} {request.path}", extra=log_data)
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process outgoing response."""
        # Skip logging for excluded paths
        if any(request.path.startswith(path) for path in self.exclude_paths):
            return response
        
        # Calculate request duration
        duration = None
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        
        # Prepare log data
        log_data = {
            'request_id': getattr(request, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2) if duration else None,
            'response_size': len(response.content) if hasattr(response, 'content') else 0
        }
        
        # Add response body if enabled
        if self.log_response and hasattr(response, 'content'):
            try:
                content = response.content.decode('utf-8')
                if content:
                    try:
                        log_data['response_body'] = json.loads(content)
                    except json.JSONDecodeError:
                        log_data['response_body'] = content[:1000]  # Limit size
            except Exception:
                log_data['response_body'] = '<Unable to decode response>'
        
        # Log with appropriate level based on status code
        if response.status_code >= 500:
            logger.error(f"Request completed with error: {request.method} {request.path}", extra=log_data)
        elif response.status_code >= 400:
            logger.warning(f"Request completed with client error: {request.method} {request.path}", extra=log_data)
        else:
            logger.info(f"Request completed: {request.method} {request.path}", extra=log_data)
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Process exceptions that occur during request processing."""
        log_data = {
            'request_id': getattr(request, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        }
        
        logger.error(f"Request failed with exception: {request.method} {request.path}", extra=log_data)
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _sanitize_headers(self, meta: Dict[str, Any]) -> Dict[str, str]:
        """Sanitize headers by removing sensitive information."""
        headers = {}
        for key, value in meta.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].lower().replace('_', '-')
                if header_name in self.sensitive_headers:
                    headers[header_name] = '***REDACTED***'
                else:
                    headers[header_name] = str(value)
        return headers


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to monitor performance metrics."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response or (lambda request: None)
        self.slow_request_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD_MS', 1000)
        self.exclude_paths = getattr(settings, 'PERFORMANCE_EXCLUDE_PATHS', [
            '/health/',
            '/metrics/',
            '/static/',
            '/media/'
        ])
    
    def process_request(self, request: HttpRequest) -> None:
        """Start performance monitoring."""
        if any(request.path.startswith(path) for path in self.exclude_paths):
            return
        
        request.perf_start_time = time.time()
        request.perf_request_id = getattr(request, 'request_id', str(uuid.uuid4()))
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Monitor response performance."""
        if any(request.path.startswith(path) for path in self.exclude_paths):
            return response
        
        if not hasattr(request, 'perf_start_time'):
            return response
        
        duration_ms = (time.time() - request.perf_start_time) * 1000
        
        # Log performance metrics
        perf_data = {
            'request_id': request.perf_request_id,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration_ms, 2),
            'is_slow': duration_ms > self.slow_request_threshold
        }
        
        if duration_ms > self.slow_request_threshold:
            logger.warning(f"Slow request detected: {request.method} {request.path}", extra=perf_data)
        else:
            logger.debug(f"Request performance: {request.method} {request.path}", extra=perf_data)
        
        # Add performance headers to response
        response['X-Response-Time'] = f"{duration_ms:.2f}ms"
        response['X-Request-ID'] = request.perf_request_id
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response or (lambda request: None)
        self.security_headers = getattr(settings, 'SECURITY_HEADERS', {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'"
        })
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add security headers to response."""
        for header, value in self.security_headers.items():
            if header not in response:
                response[header] = value
        
        return response


class CorsMiddleware(MiddlewareMixin):
    """Custom CORS middleware for API requests."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response or (lambda request: None)
        self.allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', ['*'])
        self.allowed_methods = getattr(settings, 'CORS_ALLOWED_METHODS', [
            'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'
        ])
        self.allowed_headers = getattr(settings, 'CORS_ALLOWED_HEADERS', [
            'Accept', 'Accept-Language', 'Content-Language', 'Content-Type',
            'Authorization', 'X-Requested-With', 'X-CSRFToken'
        ])
        self.max_age = getattr(settings, 'CORS_PREFLIGHT_MAX_AGE', 86400)
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Handle CORS preflight requests."""
        if request.method == 'OPTIONS':
            response = HttpResponse()
            self._add_cors_headers(request, response)
            return response
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add CORS headers to response."""
        self._add_cors_headers(request, response)
        return response
    
    def _add_cors_headers(self, request: HttpRequest, response: HttpResponse) -> None:
        """Add CORS headers to response."""
        origin = request.META.get('HTTP_ORIGIN')
        
        if origin and (self.allowed_origins == ['*'] or origin in self.allowed_origins):
            response['Access-Control-Allow-Origin'] = origin
        elif self.allowed_origins == ['*']:
            response['Access-Control-Allow-Origin'] = '*'
        
        response['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
        response['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
        response['Access-Control-Max-Age'] = str(self.max_age)
        response['Access-Control-Allow-Credentials'] = 'true'
