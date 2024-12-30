from flask import jsonify
import logging
from pythonjsonlogger import jsonlogger

# Configure logger
logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

class DocuSignError(APIError):
    """DocuSign specific errors"""
    pass

class ValidationError(APIError):
    """Validation errors"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(APIError):
    """Authentication errors"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(APIError):
    """Authorization errors"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)

def handle_api_error(error):
    """Handle API errors"""
    logger.error(f"API Error: {error.message}", extra={
        'status_code': error.status_code,
        'payload': error.payload
    })
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def handle_docusign_error(error):
    """Handle DocuSign specific errors"""
    logger.error(f"DocuSign Error: {str(error)}", extra={
        'error_type': type(error).__name__
    })
    return jsonify({
        'message': 'DocuSign operation failed',
        'error': str(error),
        'status_code': 500
    }), 500

def handle_validation_error(error):
    """Handle validation errors"""
    logger.warning(f"Validation Error: {error.message}", extra={
        'payload': error.payload
    })
    return jsonify(error.to_dict()), 400

def init_error_handlers(app):
    """Initialize error handlers for the Flask app"""
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(DocuSignError, handle_docusign_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Unexpected error occurred")
        return jsonify({
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
