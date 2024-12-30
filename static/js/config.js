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

// Determine environment based on hostname
const isProduction = window.location.hostname === 'vibrationrobotics.com';
const currentConfig = isProduction ? config.production : config.development;

export default currentConfig;
