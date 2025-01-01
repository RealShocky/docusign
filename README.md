# AI-Powered Contract Negotiation Assistant

## DocuSign Unlocked Hackathon 2024 Submission

A revolutionary AI-powered contract management system that transforms the way organizations handle agreements. By combining the power of OpenAI's language models with DocuSign's eSignature capabilities, this solution streamlines the entire contract lifecycle from drafting to signing.

[View Demo](https://github.com/RealShocky/docusign)

### Key Features

#### 1. AI-Powered Contract Analysis
- **Smart Clause Review**: Automatically analyzes contract clauses for potential issues
- **Language Optimization**: Suggests clearer, more precise wording
- **Risk Assessment**: Color-coded risk scores with detailed clause-by-clause analysis
- **Policy Compliance**: Ensures alignment with organization policies

#### 2. Interactive Negotiation Interface
- **Real-time Collaboration**: Multiple parties can review and suggest changes
- **Version Control**: Track all modifications with detailed audit trail
- **Change Impact Analysis**: AI evaluates the implications of proposed changes
- **Smart Suggestions**: Context-aware recommendations for alternative clauses

#### 3. DocuSign Integration
- **Secure eSignature Flow**: Seamless integration with DocuSign's eSignature API
- **Multiple Signer Support**: Configurable signing order and roles
- **Template Management**: Save and reuse common contract templates
- **Document Generation**: Automatic PDF conversion with Unicode support
- **Authentication**: Secure JWT-based authentication

## Quick Start

### Prerequisites
- Python 3.8+
- DocuSign Developer Account
- OpenAI API Key (GPT-4 access required)
- Node.js and npm

### Installation

1. Clone the repository:
```bash
git clone https://github.com/RealShocky/docusign.git
cd docusign
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration:
     ```
     OPENAI_API_KEY=your_openai_api_key
     DOCUSIGN_AUTH_SERVER=account-d.docusign.com
     DOCUSIGN_BASE_PATH=https://demo.docusign.net/restapi
     DATABASE_URL=sqlite:///contracts.db
     FLASK_APP=app.py
     ```

4. Set up DocuSign Integration:
   - Create a DocuSign Developer Account at [developers.docusign.com](https://developers.docusign.com)
   - Create an Integration Key (Client ID)
   - Generate RSA Keypair
   - Save private key as 'private.key'
   - Add public key to DocuSign
   - Grant consent to the application

5. Start the application:
```bash
python app.py
```

## Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **OpenAI GPT-4**: AI-powered analysis and risk assessment
- **DocuSign eSignature API**: Digital signature integration
- **FPDF**: PDF generation with Unicode support

### Frontend
- **React**: Dynamic UI components
- **Tailwind CSS**: Modern, responsive design
- **JavaScript**: Interactive features
- **Fetch API**: Asynchronous data handling

### Security
- **JWT Authentication**: Secure API access
- **Environment Variables**: Protected credentials
- **CORS**: Controlled resource sharing

## API Documentation

### Contract Analysis Endpoint
```http
POST /api/analyze
Content-Type: application/json

{
    "content": "Contract text here"
}

Response:
{
    "analysis": {
        "summary": "...",
        "suggestions": [...],
        "risks": [...]
    }
}
```

### Risk Assessment Endpoint
```http
POST /api/analyze/risks
Content-Type: application/json

{
    "content": "Contract text here"
}

Response:
{
    "overall_risk_score": 5,
    "risk_summary": "...",
    "clauses": [
        {
            "clause": "...",
            "risk_level": "high|medium|low",
            "details": "..."
        }
    ]
}
```

### Send for Signature Endpoint
```http
POST /api/send
Content-Type: application/json

{
    "contract": "Contract text",
    "signers": [
        {
            "name": "John Doe",
            "email": "john@example.com"
        }
    ]
}
```

## Changelog

### Latest Updates (December 31, 2024)

#### Features Added
- **Enhanced Risk Assessment**:
  - Added color-coded risk levels (red, yellow, green)
  - Implemented detailed clause-by-clause analysis
  - Added overall risk score calculation
  - Improved risk analysis UI with modern design

- **PDF Generation Improvements**:
  - Added Unicode character support
  - Fixed special character handling
  - Improved formatting consistency

- **UI Enhancements**:
  - Added ContractIQ logo
  - Improved layout and responsiveness
  - Removed duplicate UI elements
  - Enhanced modal designs

#### Bug Fixes
- Fixed PDF generation Unicode encoding issues
- Resolved duplicate UI elements in contract analysis
- Fixed risk assessment display issues
- Improved error handling in API endpoints

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- DocuSign Developer Team
- OpenAI API Team
- Flask Framework Community
- All contributors and testers

## Support

For support, please:
1. Check the [Issues](https://github.com/RealShocky/docusign/issues) page
2. Review existing documentation
3. Create a new issue if needed

---

Built with for the DocuSign Good Code Hackathon 2024
