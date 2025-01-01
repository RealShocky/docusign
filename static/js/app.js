// React Components
const e = React.createElement;

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'http://vibrationrobotics.com/docusign';

// Contract Templates Data with actual content
const contractTemplates = [
    {
        id: 1,
        name: 'Non-Disclosure Agreement (NDA)',
        description: 'Standard NDA template for business confidentiality',
        icon: '🔒',
        content: `MUTUAL NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (this "Agreement") is made effective as of [DATE] by and between [PARTY A] and [PARTY B].

1. Purpose
The parties wish to explore a business opportunity of mutual interest and in connection with this opportunity, each party may disclose to the other certain confidential technical and business information that the disclosing party desires the receiving party to treat as confidential.

2. Confidential Information
"Confidential Information" means any information disclosed by either party to the other party, either directly or indirectly, in writing, orally or by inspection of tangible objects, including without limitation documents, prototypes, samples, technical data, trade secrets, know-how, research, product plans, services, customer lists, markets, software, developments, inventions, processes, formulas, technology, designs, drawings, engineering, hardware configuration information, marketing, finances or other business information.

3. Term
This Agreement will terminate five (5) years after the Effective Date.

4. Governing Law
This Agreement shall be governed by and construed in accordance with the laws of [STATE/JURISDICTION].

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

[PARTY A]
By: ____________________
Name:
Title:

[PARTY B]
By: ____________________
Name:
Title:`
    },
    {
        id: 2,
        name: 'Service Agreement',
        description: 'Professional services contract template',
        icon: '📋',
        content: `SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into as of [DATE] by and between:

[SERVICE PROVIDER NAME] ("Provider")
and
[CLIENT NAME] ("Client")

1. Services
Provider agrees to provide the following services to Client: [DESCRIPTION OF SERVICES]

2. Compensation
Client agrees to compensate Provider as follows: [PAYMENT TERMS]

3. Term
This Agreement shall commence on [START DATE] and continue until [END DATE], unless terminated earlier.

4. Independent Contractor
Provider is an independent contractor, and nothing in this Agreement shall create an employer-employee relationship.

5. Confidentiality
Both parties agree to maintain the confidentiality of any proprietary information shared during the course of this Agreement.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

[SERVICE PROVIDER]
By: ____________________

[CLIENT]
By: ____________________`
    },
    {
        id: 3,
        name: 'Employment Contract',
        description: 'Standard employment agreement template',
        icon: '👥',
        content: `EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is entered into as of [DATE] by and between:

[COMPANY NAME] ("Company")
and
[EMPLOYEE NAME] ("Employee")

1. Employment
The Company agrees to employ the Employee as [POSITION] and the Employee agrees to serve in such capacity.

2. Term
This Agreement shall commence on [START DATE] and continue until [END DATE], unless terminated earlier.

3. Compensation
The Company agrees to compensate the Employee as follows: [PAYMENT TERMS]

4. Benefits
The Employee shall be entitled to the following benefits: [BENEFITS]

5. Confidentiality
The Employee agrees to maintain the confidentiality of any proprietary information shared during the course of this Agreement.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

[COMPANY]
By: ____________________

[EMPLOYEE]
By: ____________________`
    },
    {
        id: 4,
        name: 'Sales Contract',
        description: 'Template for product/service sales agreements',
        icon: '💼',
        content: `SALES AGREEMENT

This Sales Agreement (the "Agreement") is entered into as of [DATE] by and between:

[SELLER NAME] ("Seller")
and
[BUYER NAME] ("Buyer")

1. Sale
The Seller agrees to sell to the Buyer the following products/services: [DESCRIPTION OF PRODUCTS/SERVICES]

2. Price
The Buyer agrees to pay the Seller the following price: [PRICE]

3. Payment Terms
The Buyer agrees to pay the Seller as follows: [PAYMENT TERMS]

4. Delivery
The Seller agrees to deliver the products/services to the Buyer as follows: [DELIVERY TERMS]

5. Warranty
The Seller warrants that the products/services will be free from defects in material and workmanship.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

[SELLER]
By: ____________________

[BUYER]
By: ____________________`
    }
];

// Template Card Component
function TemplateCard({ template, onSelect }) {
    return e('div', {
        className: 'bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-200',
        onClick: () => onSelect(template)
    },
        e('div', { className: 'text-3xl mb-2' }, template.icon),
        e('h3', { className: 'text-lg font-semibold mb-1' }, template.name),
        e('p', { className: 'text-gray-600 text-sm' }, template.description)
    );
}

// Contract Templates Component
function ContractTemplates({ onSelectTemplate }) {
    return e('div', { className: 'bg-white rounded-xl p-6 shadow-sm' },
        e('h2', { className: 'text-xl font-semibold mb-4' }, 'Contract Templates'),
        e('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
            contractTemplates.map(template =>
                e(TemplateCard, {
                    key: template.id,
                    template: template,
                    onSelect: onSelectTemplate
                })
            )
        )
    );
}

// Debug logging
console.log('App.js loaded');
console.log('API Base URL:', API_BASE_URL);
console.log('Protocol:', window.location.protocol);
console.log('Hostname:', window.location.hostname);

function App() {
    // State
    const [showHelp, setShowHelp] = React.useState(false);
    const [showSettings, setShowSettings] = React.useState(false);
    const [showPastePrompt, setShowPastePrompt] = React.useState(false);
    const [selectedTemplate, setSelectedTemplate] = React.useState(null);
    const [analysis, setAnalysis] = React.useState(null);
    const [isAnalyzing, setIsAnalyzing] = React.useState(false);
    const [showRewritePrompt, setShowRewritePrompt] = React.useState(false);
    const [rewritePrompt, setRewritePrompt] = React.useState('');
    const [contract, setContract] = React.useState('');
    const [isRewriting, setIsRewriting] = React.useState(false);
    const [error, setError] = React.useState(null);
    const [uploadedFile, setUploadedFile] = React.useState(null);
    const [dragActive, setDragActive] = React.useState(false);
    const [signers, setSigners] = React.useState([{ name: '', email: '' }]);
    const [pasteContent, setPasteContent] = React.useState('');
    const fileInputRef = React.useRef(null);
    const textareaRef = React.useRef(null);

    // Add state for signature positions
    const [signaturePositions, setSignaturePositions] = React.useState([]);
    const [isAnalyzingPositions, setIsAnalyzingPositions] = React.useState(false);
    const [showPositionSelector, setShowPositionSelector] = React.useState(false);

    // Add state for risk analysis
    const [showRiskAnalysis, setShowRiskAnalysis] = React.useState(false);
    const [riskAnalysis, setRiskAnalysis] = React.useState(null);

    // Error Boundary
    React.useEffect(() => {
        window.onerror = (msg, url, lineNo, columnNo, error) => {
            console.error('Global error:', { msg, url, lineNo, columnNo, error });
            return false;
        };
    }, []);

    // Handle template selection
    const handleTemplateSelect = async (template) => {
        console.log('Template selected:', template);
        try {
            setIsAnalyzing(true);
            setSelectedTemplate(template);
            setContract(template.content);
            setUploadedFile('Template: ' + template.name);

            // Analyze the template content
            console.log('Sending analysis request...');
            const response = await fetch(`${API_BASE_URL}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: template.content
                })
            });

            console.log('Analysis response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Analysis error response:', errorText);
                throw new Error(`Analysis failed: ${errorText}`);
            }

            const result = await response.json();
            console.log('Analysis result:', result);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            setAnalysis(result.analysis);
            setError(null);
        } catch (error) {
            console.error('Error in handleTemplateSelect:', error);
            setError(error.message);
            setAnalysis(null);
        } finally {
            setIsAnalyzing(false);
        }
    };

    // Handle analysis
    const handleAnalyze = async (content) => {
        if (!content) {
            console.log('No content to analyze');
            return;
        }

        console.log('Starting analysis of content:', content.substring(0, 100) + '...');
        try {
            setIsAnalyzing(true);
            setAnalysis(null);
            setError(null);

            const response = await fetch(`${API_BASE_URL}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content
                })
            });

            console.log('Analysis response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Analysis error response:', errorText);
                throw new Error(`Analysis failed: ${errorText}`);
            }

            const result = await response.json();
            console.log('Analysis result:', result);

            if (result.error) {
                throw new Error(result.error);
            }

            setAnalysis(result.analysis);
        } catch (error) {
            console.error('Analysis error:', error);
            setError(error.message);
            setAnalysis(null);
        } finally {
            setIsAnalyzing(false);
        }
    };

    // Function to analyze signature positions
    const analyzeSignaturePositions = async () => {
        if (!contract) return;
        
        setIsAnalyzingPositions(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/analyze-signature-positions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: contract })
            });
            
            if (!response.ok) {
                throw new Error('Failed to analyze signature positions');
            }
            
            const result = await response.json();
            if (result.success && result.positions) {
                // Parse the positions JSON string
                const positions = typeof result.positions === 'string' 
                    ? JSON.parse(result.positions) 
                    : result.positions;
                
                setSignaturePositions(positions);
                
                // Show success message with suggestions
                setError({
                    type: 'success',
                    message: 'AI has suggested signature positions. You can review and adjust them before sending.'
                });
            }
        } catch (err) {
            console.error('Error analyzing signature positions:', err);
            setError({
                type: 'error',
                message: 'Failed to analyze signature positions: ' + err.message
            });
        } finally {
            setIsAnalyzingPositions(false);
        }
    };

    // Function to handle signature position selection
    const handlePositionSelect = (signerIndex, position) => {
        const newPositions = [...signaturePositions];
        newPositions[signerIndex] = position;
        setSignaturePositions(newPositions);
    };

    // Update the send contract function to include positions
    const handleSendContract = async () => {
        if (!contract || signers.some(s => !s.email || !s.name)) {
            setError({
                type: 'error',
                message: 'Please fill in all signer information'
            });
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contract,
                    signers,
                    signature_positions: signaturePositions
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send contract');
            }

            const result = await response.json();
            if (result.success) {
                setError({
                    type: 'success',
                    message: 'Contract sent successfully!'
                });
                // Reset form
                setContract('');
                setSigners([{ name: '', email: '' }]);
                setSignaturePositions([]);
            }
        } catch (err) {
            console.error('Error sending contract:', err);
            setError({
                type: 'error',
                message: 'Failed to send contract: ' + err.message
            });
        }
    };

    // Function to handle risk analysis
    const handleRiskAnalysis = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/analyze/risks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: contractText })
            });

            if (!response.ok) {
                throw new Error('Risk analysis failed');
            }

            const analysis = await response.json();
            setRiskAnalysis(analysis);
            setShowRiskAnalysis(true);
        } catch (error) {
            console.error('Error analyzing risks:', error);
            alert('Failed to analyze risks. Please try again.');
        }
    };

    // Render analysis section
    const renderAnalysis = () => {
        if (error) {
            return e('div', { className: 'bg-red-50 p-4 rounded-lg' },
                e('p', { className: 'text-red-600' }, error)
            );
        }

        if (isAnalyzing) {
            return e('div', { className: 'text-center p-4 bg-white rounded-xl shadow-sm border border-gray-100' },
                e('div', { className: 'flex flex-col items-center justify-center py-8' },
                    e('div', { className: 'animate-spin rounded-full h-12 w-12 border-4 border-blue-100 border-t-blue-600' }),
                    e('p', { className: 'mt-4 text-gray-600 font-medium' }, 'Analyzing your contract...')
                )
            );
        }

        if (!analysis) {
            return e('div', { className: 'bg-gray-50 p-4 rounded-lg' },
                e('p', { className: 'text-gray-600' }, 'No analysis available')
            );
        }

        // Parse the analysis text
        const parseSections = (text) => {
            const sections = {
                summary: '',
                keyPoints: '',
                suggestions: ''
            };

            const lines = text.split('\n');
            let currentSection = null;

            lines.forEach(line => {
                if (line.includes('📋 Summary')) {
                    currentSection = 'summary';
                } else if (line.includes('🎯 Key Points')) {
                    currentSection = 'keyPoints';
                } else if (line.includes('💡 Suggestions')) {
                    currentSection = 'suggestions';
                } else if (currentSection && line.trim() && !line.startsWith('##')) {
                    sections[currentSection] += line + '\n';
                }
            });

            return sections;
        };

        const sections = parseSections(analysis);

        // Format markdown text
        const formatMarkdown = (text) => {
            return text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\[(.*?)\]/g, '<em>$1</em>')
                .split('\n')
                .filter(line => line.trim())
                .map(line => {
                    // Handle numbered lists
                    if (/^\d+\./.test(line)) {
                        return `<div class="flex space-x-3 mb-3">
                            <span class="text-blue-600 font-bold">${line.match(/^\d+\./)[0]}</span>
                            <span>${line.replace(/^\d+\./, '').trim()}</span>
                        </div>`;
                    }
                    return `<p class="mb-3">${line}</p>`;
                })
                .join('');
        };

        return e('div', { className: 'space-y-8' },
            // Header
            e('div', { className: 'flex items-center justify-between mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100' },
                e('div', { className: 'flex items-center space-x-4' },
                    e('span', { className: 'text-3xl' }, '🤖'),
                    e('div', null,
                        e('h2', { className: 'text-2xl font-bold text-gray-900' }, 'AI Analysis'),
                        e('p', { className: 'text-gray-600 mt-1' }, 'Powered by GPT-4')
                    )
                ),
                e('button', {
                    className: 'px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm hover:shadow-md',
                    onClick: () => setShowRewritePrompt(true)
                }, 'Rewrite Contract')
            ),
            
            // Summary Section
            e('div', { className: 'bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow' },
                e('div', { className: 'flex items-center space-x-3 mb-6' },
                    e('span', { className: 'text-2xl' }, '📋'),
                    e('h3', { className: 'text-xl font-bold text-gray-900' }, 'Summary')
                ),
                e('div', {
                    className: 'prose max-w-none text-gray-700 leading-relaxed',
                    dangerouslySetInnerHTML: { __html: formatMarkdown(sections.summary.trim() || 'No summary available') }
                })
            ),

            // Key Points Section
            e('div', { className: 'bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow' },
                e('div', { className: 'flex items-center space-x-3 mb-6' },
                    e('span', { className: 'text-2xl' }, '🎯'),
                    e('h3', { className: 'text-xl font-bold text-gray-900' }, 'Key Points')
                ),
                e('div', {
                    className: 'prose max-w-none text-gray-700 leading-relaxed',
                    dangerouslySetInnerHTML: { __html: formatMarkdown(sections.keyPoints.trim() || 'No key points available') }
                })
            ),

            // Suggestions Section
            sections.suggestions && e('div', { className: 'bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow' },
                e('div', { className: 'flex items-center space-x-3 mb-6' },
                    e('span', { className: 'text-2xl' }, '💡'),
                    e('h3', { className: 'text-xl font-bold text-gray-900' }, 'Suggestions for Improvement')
                ),
                e('div', {
                    className: 'prose max-w-none text-gray-700 leading-relaxed',
                    dangerouslySetInnerHTML: { __html: formatMarkdown(sections.suggestions.trim()) }
                })
            ),

            // Contract Preview Section
            contract && e('div', { className: 'bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow' },
                e('div', { className: 'flex items-center space-x-3 mb-6' },
                    e('span', { className: 'text-2xl' }, '📄'),
                    e('h3', { className: 'text-xl font-bold text-gray-900' }, 'Contract Preview')
                ),
                e('div', { className: 'prose max-w-none' },
                    e('pre', { 
                        className: 'bg-gray-50 p-6 rounded-lg text-sm text-gray-800 whitespace-pre-wrap leading-relaxed overflow-x-auto border border-gray-200'
                    }, contract)
                )
            )
        );
    };

    // Render navigation
    const renderNavigation = () => {
        const steps = [
            { id: 'upload', label: 'Upload Document' },
            { id: 'analyze', label: 'Review & Analyze' },
            { id: 'signers', label: 'Add Signers' },
            { id: 'send', label: 'Send for Signature' }
        ];

        const getCurrentStep = () => {
            if (!contract) return 'upload';
            if (!analysis) return 'analyze';
            if (!signers || signers.length === 0) return 'signers';
            return 'send';
        };

        const currentStep = getCurrentStep();

        return e('nav', { className: 'flex justify-between mb-8 border-b border-gray-200' },
            steps.map(step => {
                const isActive = step.id === currentStep;
                const isPast = steps.findIndex(s => s.id === step.id) < steps.findIndex(s => s.id === currentStep);
                
                return e('div', {
                    key: step.id,
                    className: `pb-4 px-6 ${isActive ? 'text-blue-600 border-b-2 border-blue-600' : isPast ? 'text-blue-600' : 'text-gray-500'}`
                }, step.label);
            })
        );
    };

    // Load templates on mount
    React.useEffect(() => {
        fetch(`${API_BASE_URL}/api/templates`)
            .then(response => response.json())
            .catch(error => console.error('Error fetching templates:', error));
    }, []);

    // Trigger AI analysis when contract changes
    React.useEffect(() => {
        if (contract) {
            handleAnalyze(contract);
        }
    }, [contract]);

    // Handle rewrite request
    const handleRewrite = async () => {
        if (!rewritePrompt.trim()) {
            setError('Please enter rewrite instructions');
            return;
        }

        try {
            setIsRewriting(true);
            console.log('Sending rewrite request with:', {
                content: contract,
                instructions: rewritePrompt
            });

            const response = await fetch(`${API_BASE_URL}/api/rewrite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: contract,
                    instructions: rewritePrompt
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to rewrite contract');
            }

            const result = await response.json();
            if (result.error) {
                throw new Error(result.error);
            }

            setContract(result.rewritten);
            setShowRewritePrompt(false);
            setRewritePrompt('');
            setError(null);
        } catch (error) {
            console.error('Rewrite error:', error);
            setError(error.message);
        } finally {
            setIsRewriting(false);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileUpload = (event) => {
        if (event.target.files && event.target.files[0]) {
            handleFile(event.target.files[0]);
        }
    };

    const handleFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            setContract(e.target.result);
            setUploadedFile(file.name);
        };
        reader.readAsText(file);
    };

    const handlePaste = () => {
        setShowPastePrompt(true);
    };

    const handlePasteSubmit = () => {
        if (pasteContent) {
            setContract(pasteContent);
            setUploadedFile('Pasted Content');
            setShowPastePrompt(false);
            setPasteContent('');
        }
    };

    const handlePasteCancel = () => {
        setShowPastePrompt(false);
        setPasteContent('');
    };

    const handleHelp = () => {
        setShowHelp(true);
    };

    const handleSettings = () => {
        setShowSettings(true);
    };

    const handleCloseModal = () => {
        setShowHelp(false);
        setShowSettings(false);
    };

    const handleAddSigner = () => {
        setSigners([...signers, { name: '', email: '' }]);
    };

    const handleRemoveSigner = (index) => {
        setSigners(signers.filter((_, i) => i !== index));
    };

    const handleSignerChange = (index, field, value) => {
        const newSigners = [...signers];
        newSigners[index][field] = value;
        setSigners(newSigners);
    };

    // Risk Analysis Button Component
    function RiskAnalysisButton({ onAnalyze }) {
        return e('button', {
            className: 'btn btn-warning ms-2',
            onClick: onAnalyze,
            title: 'Analyze contract risks'
        }, '🔍 Risk Analysis');
    }

    // Risk Analysis Modal Component
    function RiskAnalysisModal({ isOpen, onClose, analysis }) {
        if (!isOpen) return null;

        const getRiskColor = (level) => {
            const colors = {
                high: '#ffebee',
                medium: '#fff3e0',
                low: '#e8f5e9'
            };
            return colors[level] || '#ffffff';
        };

        return e('div', {
            className: 'modal show d-block',
            tabIndex: '-1'
        },
            e('div', { className: 'modal-dialog modal-lg' },
                e('div', { className: 'modal-content' },
                    e('div', { className: 'modal-header' },
                        e('h5', { className: 'modal-title' }, '📊 Risk Analysis Report'),
                        e('button', {
                            type: 'button',
                            className: 'btn-close',
                            onClick: onClose
                        })
                    ),
                    e('div', { className: 'modal-body' },
                        e('div', { className: 'mb-4' },
                            e('h6', { className: 'fw-bold' }, 'Overall Risk Score: ',
                                e('span', {
                                    className: `badge ${analysis.overall_risk_score > 7 ? 'bg-danger' : analysis.overall_risk_score > 4 ? 'bg-warning' : 'bg-success'}`
                                }, `${analysis.overall_risk_score}/10`)
                            ),
                            e('p', { className: 'mt-2' }, analysis.risk_summary)
                        ),
                        e('div', { className: 'mb-4' },
                            e('h6', { className: 'fw-bold' }, 'Clause Analysis'),
                            e('div', { className: 'list-group' },
                                analysis.clauses.map((clause, index) =>
                                    e('div', {
                                        key: index,
                                        className: 'list-group-item',
                                        style: { backgroundColor: getRiskColor(clause.risk_level) }
                                    },
                                        e('h6', { className: 'mb-2' }, `Risk Level: `,
                                            e('span', {
                                                className: `badge ${clause.risk_level === 'high' ? 'bg-danger' : clause.risk_level === 'medium' ? 'bg-warning' : 'bg-success'}`
                                            }, clause.risk_level.toUpperCase())
                                        ),
                                        e('div', { className: 'mb-2' },
                                            e('strong', {}, 'Clause: '),
                                            clause.text
                                        ),
                                        e('div', { className: 'mb-2' },
                                            e('strong', {}, 'Risk Factors:'),
                                            e('ul', {},
                                                clause.risk_factors.map((factor, i) =>
                                                    e('li', { key: i }, factor)
                                                )
                                            )
                                        ),
                                        e('div', { className: 'mb-2' },
                                            e('strong', {}, 'Suggestions:'),
                                            e('ul', {},
                                                clause.suggestions.map((suggestion, i) =>
                                                    e('li', { key: i }, suggestion)
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        e('div', { className: 'mb-4' },
                            e('h6', { className: 'fw-bold' }, 'Key Concerns'),
                            e('ul', { className: 'list-group' },
                                analysis.key_concerns.map((concern, index) =>
                                    e('li', {
                                        key: index,
                                        className: 'list-group-item list-group-item-warning'
                                    }, concern)
                                )
                            )
                        )
                    )
                )
            )
        );
    }

    const renderPositionSelector = () => {
        if (!showPositionSelector) return null;
        
        return e('div', { className: 'position-selector' },
            e('h3', null, 'Select Signature Positions'),
            signers.map((signer, index) => 
                e('div', { key: index, className: 'signer-position' },
                    e('h4', null, signer.name || `Signer ${index + 1}`),
                    signaturePositions[index] && e('div', { className: 'position-info' },
                        e('p', null, 
                            e('strong', null, 'Description:'), 
                            ' ', 
                            signaturePositions[index].description
                        ),
                        e('p', null, 
                            e('strong', null, 'Location:'), 
                            ' ', 
                            signaturePositions[index].anchor_text
                        ),
                        e('p', null, 
                            e('strong', null, 'Alignment:'), 
                            ' ', 
                            signaturePositions[index].align
                        )
                    )
                )
            )
        );
    };

    const renderRewritePrompt = () => {
        if (!showRewritePrompt) return null;

        return e('div', {
            className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
        },
            e('div', { className: 'bg-white rounded-xl p-6 max-w-2xl w-full' },
                e('div', { className: 'flex justify-between items-center mb-4' },
                    e('h2', { className: 'text-xl font-semibold' }, 'Rewrite Contract'),
                    e('button', {
                        className: 'text-gray-500 hover:text-gray-700',
                        onClick: () => setShowRewritePrompt(false)
                    }, '×')
                ),
                e('p', { className: 'mb-4 text-gray-600' }, 
                    'Enter your instructions for rewriting the contract. Be specific about what changes you want to make.'
                ),
                e('textarea', {
                    className: 'w-full h-32 p-3 border rounded-lg mb-4',
                    placeholder: 'Example: Make the language more formal and add a confidentiality clause',
                    value: rewritePrompt,
                    onChange: (e) => setRewritePrompt(e.target.value)
                }),
                e('div', { className: 'flex justify-end space-x-3' },
                    e('button', {
                        className: 'px-4 py-2 text-gray-600 border rounded hover:bg-gray-50',
                        onClick: () => setShowRewritePrompt(false)
                    }, 'Cancel'),
                    e('button', {
                        className: `px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 ${isRewriting ? 'opacity-50 cursor-not-allowed' : ''}`,
                        onClick: handleRewrite,
                        disabled: isRewriting
                    }, isRewriting ? 'Rewriting...' : 'Rewrite')
                )
            )
        );
    };

    const renderSettings = () => {
        if (!showSettings) return null;

        return e('div', {
            className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
        },
            e('div', { className: 'bg-white rounded-xl p-6 max-w-2xl w-full' },
                e('div', { className: 'flex justify-between items-center mb-4' },
                    e('h2', { className: 'text-xl font-semibold' }, 'Settings'),
                    e('button', {
                        className: 'text-gray-500 hover:text-gray-700',
                        onClick: () => setShowSettings(false)
                    }, '×')
                ),
                e('div', { className: 'space-y-4' },
                    e('div', null,
                        e('h3', { className: 'font-medium mb-2' }, 'API Configuration'),
                        e('p', { className: 'text-sm text-gray-600 mb-2' }, 
                            'Current API URL: ', API_BASE_URL
                        )
                    ),
                    e('div', null,
                        e('h3', { className: 'font-medium mb-2' }, 'Default Template'),
                        e('select', {
                            className: 'w-full p-2 border rounded',
                            value: selectedTemplate?.id || '',
                            onChange: (e) => {
                                const template = contractTemplates.find(t => t.id === parseInt(e.target.value));
                                if (template) handleTemplateSelect(template);
                            }
                        },
                            e('option', { value: '' }, 'Select a template'),
                            contractTemplates.map(template =>
                                e('option', { key: template.id, value: template.id }, template.name)
                            )
                        )
                    )
                ),
                e('div', { className: 'flex justify-end mt-6' },
                    e('button', {
                        className: 'px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700',
                        onClick: () => setShowSettings(false)
                    }, 'Close')
                )
            )
        );
    };

    const renderSigners = () => {
        return e('div', { className: 'bg-white p-6 rounded-xl shadow-sm border border-gray-100' },
            e('div', { className: 'flex items-center justify-between mb-6' },
                e('h3', { className: 'text-xl font-bold text-gray-900' }, 'Signers'),
                e('button', {
                    className: 'text-blue-600 hover:text-blue-700 font-medium flex items-center',
                    onClick: () => {
                        setSigners([...signers, { name: '', email: '' }]);
                    }
                },
                    e('span', { className: 'mr-2' }, '+'),
                    'Add Signer'
                )
            ),
            signers.map((signer, index) => (
                e('div', { key: index, className: 'flex gap-4 mb-4' },
                    e('input', {
                        type: 'text',
                        placeholder: 'Name',
                        className: 'flex-1 p-2 border border-gray-300 rounded-lg',
                        value: signer.name,
                        onChange: (e) => {
                            const newSigners = [...signers];
                            newSigners[index].name = e.target.value;
                            setSigners(newSigners);
                        }
                    }),
                    e('input', {
                        type: 'email',
                        placeholder: 'Email',
                        className: 'flex-1 p-2 border border-gray-300 rounded-lg',
                        value: signer.email,
                        onChange: (e) => {
                            const newSigners = [...signers];
                            newSigners[index].email = e.target.value;
                            setSigners(newSigners);
                        }
                    }),
                    e('button', {
                        className: 'text-red-600 hover:text-red-700',
                        onClick: () => {
                            const newSigners = signers.filter((_, i) => i !== index);
                            setSigners(newSigners);
                        }
                    }, '×')
                )
            )),
            // Send for Signature button
            signers.length > 0 && e('div', { className: 'mt-6 flex justify-end' },
                e('button', {
                    className: 'px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm hover:shadow-md',
                    onClick: handleSendContract
                }, 'Send for Signature')
            )
        );
    };

    const Header = () => {
        return e('div', { className: 'mb-8' },
            e('div', { className: 'bg-blue-600 text-white p-4 text-center' },
                e('h1', { className: 'text-2xl font-bold' }, 'ContractIQ'),
                e('p', { className: 'text-sm mt-1' }, 'AI-Powered Contract Management')
            ),
            e('nav', { className: 'bg-white border-b' },
                e('div', { className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8' },
                    e('div', { className: 'flex justify-between h-16' },
                        e('div', { className: 'flex' },
                            e('div', { className: 'flex-shrink-0 flex items-center' },
                                e('img', {
                                    className: 'h-8 w-auto',
                                    src: 'static/images/ContractIQ.svg',
                                    alt: 'ContractIQ'
                                })
                            )
                        ),
                        e('div', { className: 'flex items-center' },
                            e('button', {
                                className: 'p-2 text-gray-600 hover:text-gray-800',
                                onClick: () => setShowHelp(true)
                            }, '?'),
                            e('button', {
                                className: 'p-2 ml-2 text-gray-600 hover:text-gray-800',
                                onClick: () => setShowSettings(true)
                            }, '⚙️')
                        )
                    )
                )
            )
        );
    };

    const renderContractActions = () => {
        return e('div', { className: 'flex flex-wrap gap-2 mt-4' },
            e('button', {
                className: 'px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700',
                onClick: handleAnalyze,
                disabled: !contract || isAnalyzing
            }, isAnalyzing ? 'Analyzing...' : 'Analyze Contract'),
            e('button', {
                className: 'px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700',
                onClick: handleRiskAnalysis,
                disabled: !contract || isAnalyzing
            }, '🔍 Risk Analysis'),
            e('button', {
                className: 'px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700',
                onClick: () => setShowRewritePrompt(true),
                disabled: !contract
            }, '✏️ Rewrite')
        );
    };

    return e('div', { className: 'min-h-screen bg-gray-50' },
        // Header
        e(Header),
        // Progress Steps
        renderNavigation(),
        // Main Content
        e('div', { className: 'container mx-auto px-4 grid grid-cols-1 lg:grid-cols-3 gap-8' },
            // Left Column - Templates
            e('div', { className: 'lg:col-span-1' },
                e(ContractTemplates, { onSelectTemplate: handleTemplateSelect })
            ),

            // Middle Column - Document Upload and Analysis
            e('div', { className: 'lg:col-span-1' },
                e('div', { className: 'bg-white p-6 rounded-xl shadow-md' },
                    // Document Upload Section
                    e('h2', { className: 'text-xl font-semibold mb-4' }, 'Document Upload'),
                    uploadedFile && e('div', { className: 'mb-4 text-green-600' },
                        'File loaded: ', uploadedFile
                    ),
                    
                    // Upload Area
                    !uploadedFile && e('div', {
                        className: `upload-area rounded-lg p-8 text-center ${dragActive ? 'drag-active' : ''}`,
                        onDragEnter: handleDrag,
                        onDragLeave: handleDrag,
                        onDragOver: handleDrag,
                        onDrop: handleDrop
                    },
                        e('div', { key: 'upload-prompt' },
                            e('p', { className: 'text-gray-600 mb-4' },
                                'Drag and drop your document here, or ',
                                e('button', {
                                    className: 'text-blue-600 hover:text-blue-700',
                                    onClick: () => fileInputRef.current.click()
                                }, 'browse'),
                                ' to upload'
                            ),
                            e('input', {
                                type: 'file',
                                ref: fileInputRef,
                                onChange: handleFileUpload,
                                className: 'hidden'
                            })
                        ),
                        e('div', { key: 'divider', className: 'my-4 flex items-center justify-center' },
                            e('span', { className: 'text-gray-400' }, 'or')
                        ),
                        e('button', {
                            key: 'paste-button',
                            className: 'flex items-center justify-center mx-auto text-gray-600 hover:text-gray-700',
                            onClick: handlePaste
                        },
                            e('svg', { className: 'w-5 h-5 mr-2', fill: 'currentColor', viewBox: '0 0 20 20' },
                                e('path', { d: 'M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z' }),
                                e('path', { d: 'M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z' })
                            ),
                            'Paste Content'
                        )
                    )
                ),

                // Analysis Section
                contract && e('div', { className: 'bg-blue-50 p-6 rounded-xl mt-6' },
                    e('div', { className: 'flex items-center justify-between mb-4' },
                        e('div', { className: 'flex items-center gap-3' },
                            e('div', null,
                                e('h3', { className: 'text-lg font-semibold' }, 'AI Analysis'),
                                e('p', { className: 'text-sm text-gray-600' }, 'Powered by GPT-4')
                            )
                        )
                    ),
                    renderContractActions(),
                    analysis && e('div', { className: 'mt-4' }, renderAnalysis())
                )
            ),

            // Right Column - Contract Preview and Signers
            e('div', { className: 'lg:col-span-1' },
                contract && e('div', { className: 'bg-white p-6 rounded-xl shadow-md' },
                    e('h2', { className: 'text-xl font-semibold mb-4' }, 'Contract Preview'),
                    e('textarea', {
                        ref: textareaRef,
                        value: contract,
                        onChange: e => setContract(e.target.value),
                        className: 'w-full h-64 p-4 border rounded-lg font-mono text-sm',
                        spellCheck: false
                    })
                ),
                renderSigners(),
                renderPositionSelector()
            )
        ),

        // Help Modal
        showHelp && e('div', { className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4' },
            e('div', { className: 'bg-white rounded-xl p-6 max-w-2xl w-full' },
                e('div', { className: 'flex justify-between items-center mb-4' },
                    e('h2', { className: 'text-xl font-semibold' }, 'Help'),
                    e('button', { onClick: handleCloseModal }, '×')
                ),
                e('div', { className: 'prose' },
                    e('h3', null, 'Getting Started'),
                    e('p', null, 'Welcome to ContractIQ! Here\'s how to get started:'),
                    e('ol', null,
                        e('li', null, 'Upload a document by dragging and dropping it into the upload area, or click "browse" to select a file.'),
                        e('li', null, 'Alternatively, use one of our pre-made contract templates by selecting it from the templates section.'),
                        e('li', null, 'Review your contract in the preview section and make any necessary changes.'),
                        e('li', null, 'Add signers by clicking the "Add Signer" button and entering their details.'),
                        e('li', null, 'Send the contract for signatures when ready.')
                    ),
                    e('h3', null, 'Features'),
                    e('ul', null,
                        e('li', null, 'Drag and drop file upload'),
                        e('li', null, 'Contract templates'),
                        e('li', null, 'Contract preview and editing'),
                        e('li', null, 'Multiple signers support'),
                        e('li', null, 'Secure electronic signatures')
                    )
                )
            )
        ),

        // Settings Modal
        showSettings && renderSettings(),

        // Paste Content Modal
        showPastePrompt && e('div', { className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4' },
            e('div', { className: 'bg-white rounded-xl p-6 max-w-2xl w-full' },
                e('div', { className: 'flex justify-between items-center mb-4' },
                    e('h2', { className: 'text-xl font-semibold' }, 'Paste Contract Content'),
                    e('button', {
                        className: 'text-gray-500 hover:text-gray-700',
                        onClick: handlePasteCancel
                    }, '×')
                ),
                e('textarea', {
                    className: 'w-full h-64 p-4 border rounded-lg mb-4',
                    placeholder: 'Paste your contract content here...',
                    value: pasteContent,
                    onChange: (e) => setPasteContent(e.target.value)
                }),
                e('div', { className: 'flex justify-end space-x-4' },
                    e('button', {
                        className: 'px-4 py-2 text-gray-600 hover:text-gray-800',
                        onClick: handlePasteCancel
                    }, 'Cancel'),
                    e('button', {
                        className: 'px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700',
                        onClick: handlePasteSubmit,
                        disabled: !pasteContent
                    }, 'Submit')
                )
            )
        ),

        renderRewritePrompt(),
        showRiskAnalysis && e(RiskAnalysisModal, {
            isOpen: showRiskAnalysis,
            onClose: () => setShowRiskAnalysis(false),
            analysis: riskAnalysis
        })
    );
}

// Initialize the app
window.addEventListener('load', () => {
    const rootElement = document.getElementById('root');
    if (rootElement) {
        const app = e(App);
        ReactDOM.render(app, rootElement);
    }
});
