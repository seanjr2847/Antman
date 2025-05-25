"""
Error handling middleware for Django applications.
"""
import logging
import traceback
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .exceptions import AntmanBaseException
from .handlers import ErrorHandler


logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Middleware for centralized error handling."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response or (lambda request: None)
        self.error_handler = ErrorHandler()
        self.debug = getattr(settings, 'DEBUG', False)
    
    def process_exception(self, request, exception):
        """Process exceptions and return appropriate responses."""
        try:
            # Log the exception
            logger.error(
                f"Exception in {request.method} {request.path}: {str(exception)}",
                exc_info=True,
                extra={
                    'request': request,
                    'user': getattr(request, 'user', None),
                    'exception_type': type(exception).__name__
                }
            )
            
            # Handle Antman custom exceptions
            if isinstance(exception, AntmanBaseException):
                return self._handle_antman_exception(request, exception)
            
            # Handle other exceptions
            return self._handle_generic_exception(request, exception)
            
        except Exception as e:
            logger.critical(f"Error in error handling middleware: {str(e)}", exc_info=True)
            return self._fallback_error_response(request)
    
    def _handle_antman_exception(self, request, exception):
        """Handle Antman custom exceptions."""
        error_data = exception.to_dict()
        
        if self._is_api_request(request):
            return JsonResponse(
                error_data,
                status=exception.status_code,
                safe=False
            )
        else:
            # For web requests, you might want to render an error template
            return JsonResponse(error_data, status=exception.status_code)
    
    def _handle_generic_exception(self, request, exception):
        """Handle generic Python/Django exceptions."""
        if self.debug:
            # In debug mode, let Django handle it normally
            return None
        
        error_data = {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'code': 'INTERNAL_ERROR'
        }
        
        if self._is_api_request(request):
            return JsonResponse(error_data, status=500)
        else:
            return JsonResponse(error_data, status=500)
    
    def _fallback_error_response(self, request):
        """Fallback error response when error handling fails."""
        error_data = {
            'error': 'Critical error',
            'message': 'A critical error occurred in error handling',
            'code': 'CRITICAL_ERROR'
        }
        
        return JsonResponse(error_data, status=500)
    
    def _is_api_request(self, request):
        """Check if the request is an API request."""
        content_type = request.META.get('CONTENT_TYPE', '')
        accept = request.META.get('HTTP_ACCEPT', '')
        
        return (
            'application/json' in content_type or
            'application/json' in accept or
            request.path.startswith('/api/')
        )


class APIErrorHandlingMiddleware(MiddlewareMixin):
    """Specialized middleware for API error handling."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response or (lambda request: None)
        self.error_handler = ErrorHandler()
    
    def process_exception(self, request, exception):
        """Process exceptions for API requests only."""
        if not self._is_api_request(request):
            return None
        
        try:
            response_data = self.error_handler.handle_error(request, exception)
            return JsonResponse(
                response_data['data'],
                status=response_data['status_code']
            )
        except Exception as e:
            logger.error(f"Error in API error handling: {str(e)}", exc_info=True)
            return JsonResponse(
                {
                    'error': 'Internal server error',
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR'
                },
                status=500
            )
    
    def _is_api_request(self, request):
        """Check if the request is an API request."""
        return (
            request.path.startswith('/api/') or
            'application/json' in request.META.get('CONTENT_TYPE', '') or
            'application/json' in request.META.get('HTTP_ACCEPT', '')
        )


class RequestLoggingErrorMiddleware(MiddlewareMixin):
    """Middleware that logs request details when errors occur."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response or (lambda request: None)
    
    def process_exception(self, request, exception):
        """Log detailed request information when exceptions occur."""
        try:
            request_data = {
                'method': request.method,
                'path': request.path,
                'user': str(getattr(request, 'user', 'Anonymous')),
                'ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'headers': dict(request.headers),
                'exception': str(exception),
                'exception_type': type(exception).__name__
            }
            
            # Add request body for POST/PUT/PATCH requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body'):
                        request_data['body'] = request.body.decode('utf-8')[:1000]  # Limit size
                except Exception:
                    request_data['body'] = '<Unable to decode body>'
            
            logger.error(
                f"Request error: {exception}",
                extra={'request_data': request_data},
                exc_info=True
            )
            
        except Exception as e:
            logger.error(f"Error in request logging middleware: {str(e)}")
        
        # Don't handle the exception, just log it
        return None
    
    def _get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
