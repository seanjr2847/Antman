"""
Error handlers for comprehensive error management.
"""
import logging
import traceback
from typing import Dict, Any, Optional, Union
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, DatabaseError as DjangoDatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .exceptions import (
    AntmanBaseException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ExternalServiceError,
    RateLimitExceededError,
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    CacheError,
    FileSystemError
)


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Main error handler for the application."""
    
    def __init__(self):
        self.error_mappings = {
            DjangoValidationError: self._handle_django_validation_error,
            IntegrityError: self._handle_integrity_error,
            DjangoDatabaseError: self._handle_django_database_error,
            PermissionError: self._handle_permission_error,
            FileNotFoundError: self._handle_file_not_found_error,
            ConnectionError: self._handle_connection_error,
            TimeoutError: self._handle_timeout_error,
            ValueError: self._handle_value_error,
            KeyError: self._handle_key_error,
            AttributeError: self._handle_attribute_error,
        }
    
    def handle_error(
        self, 
        request: HttpRequest, 
        exception: Exception,
        include_traceback: bool = False
    ) -> Union[JsonResponse, HttpResponse]:
        """Handle any exception and return appropriate response."""
        
        # Log the error
        self._log_error(request, exception)
        
        # Handle Antman custom exceptions
        if isinstance(exception, AntmanBaseException):
            return self._handle_antman_exception(exception, include_traceback)
        
        # Handle known Django/Python exceptions
        if type(exception) in self.error_mappings:
            handler = self.error_mappings[type(exception)]
            return handler(exception, include_traceback)
        
        # Handle unknown exceptions
        return self._handle_unknown_exception(exception, include_traceback)
    
    def _handle_antman_exception(
        self, 
        exception: AntmanBaseException, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle custom Antman exceptions."""
        error_data = exception.to_dict()
        
        if include_traceback:
            error_data['traceback'] = traceback.format_exc()
        
        return JsonResponse(
            error_data,
            status=exception.http_status_code,
            safe=False
        )
    
    def _handle_django_validation_error(
        self, 
        exception: DjangoValidationError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle Django validation errors."""
        field_errors = {}
        non_field_errors = []
        
        if hasattr(exception, 'error_dict'):
            # Field-specific errors
            for field, errors in exception.error_dict.items():
                field_errors[field] = [str(error) for error in errors]
        elif hasattr(exception, 'error_list'):
            # Non-field errors
            non_field_errors = [str(error) for error in exception.error_list]
        else:
            non_field_errors = [str(exception)]
        
        validation_error = ValidationError(
            message="Validation failed",
            field_errors=field_errors,
            details={'non_field_errors': non_field_errors}
        )
        
        return self._handle_antman_exception(validation_error, include_traceback)
    
    def _handle_integrity_error(
        self, 
        exception: IntegrityError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle database integrity errors."""
        db_error = DatabaseError(
            message="Database integrity constraint violated",
            operation="INSERT/UPDATE",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(db_error, include_traceback)
    
    def _handle_django_database_error(
        self, 
        exception: DjangoDatabaseError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle Django database errors."""
        db_error = DatabaseError(
            message="Database operation failed",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(db_error, include_traceback)
    
    def _handle_permission_error(
        self, 
        exception: PermissionError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle permission errors."""
        auth_error = AuthorizationError(
            message="Insufficient permissions",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(auth_error, include_traceback)
    
    def _handle_file_not_found_error(
        self, 
        exception: FileNotFoundError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle file not found errors."""
        fs_error = FileSystemError(
            message="File not found",
            file_path=getattr(exception, 'filename', None),
            operation="READ",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(fs_error, include_traceback)
    
    def _handle_connection_error(
        self, 
        exception: ConnectionError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle connection errors."""
        service_error = ExternalServiceError(
            message="Connection failed",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(service_error, include_traceback)
    
    def _handle_timeout_error(
        self, 
        exception: TimeoutError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle timeout errors."""
        service_error = ExternalServiceError(
            message="Operation timed out",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(service_error, include_traceback)
    
    def _handle_value_error(
        self, 
        exception: ValueError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle value errors."""
        validation_error = ValidationError(
            message="Invalid value provided",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(validation_error, include_traceback)
    
    def _handle_key_error(
        self, 
        exception: KeyError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle key errors."""
        validation_error = ValidationError(
            message=f"Missing required key: {str(exception)}",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(validation_error, include_traceback)
    
    def _handle_attribute_error(
        self, 
        exception: AttributeError, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle attribute errors."""
        config_error = ConfigurationError(
            message="Configuration or attribute error",
            details={'original_error': str(exception)}
        )
        return self._handle_antman_exception(config_error, include_traceback)
    
    def _handle_unknown_exception(
        self, 
        exception: Exception, 
        include_traceback: bool = False
    ) -> JsonResponse:
        """Handle unknown exceptions."""
        unknown_error = AntmanBaseException(
            message="An unexpected error occurred",
            error_code="UNKNOWN_ERROR",
            details={
                'exception_type': type(exception).__name__,
                'original_error': str(exception)
            }
        )
        
        return self._handle_antman_exception(unknown_error, include_traceback)
    
    def _log_error(self, request: HttpRequest, exception: Exception) -> None:
        """Log error details."""
        error_info = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'request_path': request.path,
            'request_method': request.method,
            'user': getattr(request, 'user', None),
            'traceback': traceback.format_exc()
        }
        
        if isinstance(exception, AntmanBaseException):
            logger.error(
                f"Antman Exception: {exception.error_code} - {exception.message}",
                extra=error_info
            )
        else:
            logger.error(
                f"Unhandled Exception: {type(exception).__name__} - {str(exception)}",
                extra=error_info
            )


# Global error handler instance
error_handler = ErrorHandler()


def custom_exception_handler(exc, context):
    """Custom DRF exception handler."""
    # Call REST framework's default exception handler first
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        return response
    
    # Handle exceptions not handled by DRF
    request = context.get('request')
    if request:
        json_response = error_handler.handle_error(request, exc)
        return Response(
            json_response.content,
            status=json_response.status_code
        )
    
    # Fallback for cases without request context
    if isinstance(exc, AntmanBaseException):
        return Response(
            exc.to_dict(),
            status=exc.http_status_code
        )
    
    return Response(
        {
            'error_code': 'UNKNOWN_ERROR',
            'message': 'An unexpected error occurred',
            'details': {'original_error': str(exc)}
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def handle_404(request, exception):
    """Handle 404 errors."""
    not_found_error = ResourceNotFoundError(
        message="The requested resource was not found",
        resource_type="URL",
        resource_id=request.path
    )
    return error_handler.handle_error(request, not_found_error)


def handle_500(request):
    """Handle 500 errors."""
    server_error = AntmanBaseException(
        message="Internal server error",
        error_code="INTERNAL_SERVER_ERROR"
    )
    return error_handler.handle_error(request, server_error)


def handle_403(request, exception):
    """Handle 403 errors."""
    forbidden_error = AuthorizationError(
        message="Access forbidden",
        details={'path': request.path}
    )
    return error_handler.handle_error(request, forbidden_error)


def handle_400(request, exception):
    """Handle 400 errors."""
    bad_request_error = ValidationError(
        message="Bad request",
        details={'path': request.path}
    )
    return error_handler.handle_error(request, bad_request_error)
