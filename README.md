# ContractIQ

ContractIQ streamlines contract negotiations with AI-powered insights and DocuSign integration.

## 🚀 Demo

Check out our live demo: [ContractIQ Demo](http://vibrationrobotics.com/docusign)

## ✨ Features

- 📄 AI-powered contract analysis
- 📝 Pre-built contract templates
- ✍️ Seamless DocuSign integration
- 👥 Multiple signer support
- 🔒 Secure document handling
- 💡 Real-time collaboration

## 🛠️ Technologies Used

- Python, Flask, JavaScript, HTML5/CSS3, DocuSign API, OpenAI API, SQLite, JWT Authentication, Bootstrap, AJAX, CORS, FPDF, SQLAlchemy, Redis, Git

## 🚦 Getting Started

1. Clone the repository:
```bash
git clone https://github.com/RealShocky/docusign.git
cd docusign
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials:
# - DOCUSIGN_INTEGRATION_KEY
# - DOCUSIGN_USER_ID
# - DOCUSIGN_ACCOUNT_ID
# - DOCUSIGN_PRIVATE_KEY_PATH
# - OPENAI_API_KEY
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access the web interface at `http://localhost:5000`

## 🧪 Testing Instructions

1. Start the Flask server
2. Upload a sample NDA or use the pre-built template
3. Test AI analysis with the provided prompt
4. Add test signers (use your email)
5. Verify DocuSign integration

## 📚 API Documentation

### DocuSign Integration
- JWT Authentication
- Envelope creation
- Multiple signer workflow
- Template management

### OpenAI Integration
- Contract analysis
- Improvement suggestions
- Language modernization

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- DocuSign for the eSignature API
- OpenAI for the GPT API
- All contributors to this project
