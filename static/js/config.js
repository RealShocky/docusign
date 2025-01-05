const config = {
    development: {
        baseUrl: 'http://localhost:5000',
        apiPath: '/api'
    },
    production: {
        baseUrl: 'https://vibrationrobotics.com',
        apiPath: '/docusign/api'
    }
};

// API Configuration
const SERVER_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'http://vibrationrobotics.com/docusign';

// DocuSign Configuration
const DOCUSIGN_CONFIG = {
    webForms: {
        environment: 'demo', // or 'production'
        accountId: 'YOUR_ACCOUNT_ID', // Will be replaced by actual account ID
        userId: 'YOUR_USER_ID', // Will be replaced by actual user ID
        integratorKey: 'YOUR_INTEGRATOR_KEY' // Will be replaced by actual integrator key
    }
};

// Determine environment based on hostname
const isProduction = window.location.hostname === 'vibrationrobotics.com';
const currentConfig = isProduction ? config.production : config.development;

// Export configurations
export { SERVER_URL, DOCUSIGN_CONFIG, currentConfig };
