import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
    
    # Session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Will be set in app.py
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS
    CORS_ORIGINS = [
        'https://vibrationrobotics.com',
        'https://www.vibrationrobotics.com'
    ]
    if os.getenv('FLASK_ENV') == 'development':
        CORS_ORIGINS.append('http://localhost:5000')
    
    # DocuSign
    DOCUSIGN_INTEGRATION_KEY = os.getenv('DOCUSIGN_INTEGRATION_KEY')
    DOCUSIGN_CLIENT_SECRET = os.getenv('DOCUSIGN_CLIENT_SECRET')
    DOCUSIGN_ACCOUNT_ID = os.getenv('DOCUSIGN_ACCOUNT_ID')
    DOCUSIGN_AUTH_SERVER = 'https://account-d.docusign.com'
    DOCUSIGN_CALLBACK_URL = 'https://vibrationrobotics.com/callback'
    
    # Logging
    LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
