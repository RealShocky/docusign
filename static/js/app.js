// Make React.createElement global
const e = React.createElement;

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'https://vibrationrobotics.com/docusign';

// Contract Templates Data
const templates = [
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
"Confidential Information" means any information disclosed by either party to the other party, either directly or indirectly, in writing, orally or by inspection of tangible objects.

3. Term
This Agreement will terminate five (5) years after the Effective Date.`
    },
    {
        id: 2,
        name: 'Service Agreement',
        description: 'Professional services contract template',
        icon: '📋',
        content: `SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into as of [DATE] by and between [PROVIDER] and [CLIENT].

1. Services
Provider agrees to provide the following services to Client: [DESCRIPTION OF SERVICES]

2. Compensation
Client agrees to compensate Provider as follows: [PAYMENT TERMS]

3. Term
This Agreement shall commence on [START DATE] and continue until [END DATE], unless terminated earlier.`
    },
    {
        id: 3,
        name: 'Employment Contract',
        description: 'Standard employment agreement template',
        icon: '👥',
        content: `EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is entered into as of [DATE] by and between [EMPLOYER] and [EMPLOYEE].

1. Position and Duties
Employee shall serve in the position of [POSITION] and shall perform the duties assigned by Employer.

2. Compensation
Employer shall pay Employee a base salary of [AMOUNT] per year, payable in accordance with Employer's standard payroll practices.

3. Benefits
Employee shall be entitled to participate in all employee benefit plans and programs offered by Employer.`
    },
    {
        id: 4,
        name: 'Sales Contract',
        description: 'Template for product/service sales agreements',
        icon: '🛍️',
        content: `SALES AGREEMENT

This Sales Agreement (the "Agreement") is entered into as of [DATE] by and between [SELLER] and [BUYER].

1. Products/Services
Seller agrees to sell and Buyer agrees to purchase the following: [DESCRIPTION]

2. Price and Payment
The total purchase price shall be [AMOUNT], payable as follows: [PAYMENT TERMS]

3. Delivery
Seller shall deliver the products/services as follows: [DELIVERY TERMS]`
    },
    {
        id: 5,
        name: 'Lease Agreement',
        description: 'Property rental/lease contract template',
        icon: '🏠',
        content: `LEASE AGREEMENT

This Lease Agreement (the "Agreement") is entered into as of [DATE] by and between [LANDLORD] and [TENANT].

1. Property
Landlord leases to Tenant the property located at: [ADDRESS]

2. Term
The lease term shall be [DURATION] beginning on [START DATE] and ending on [END DATE].

3. Rent
Tenant shall pay rent of [AMOUNT] per month, due on the [DAY] of each month.`
    },
    {
        id: 6,
        name: 'Partnership Agreement',
        description: 'Business partnership contract template',
        icon: '🤝',
        content: `PARTNERSHIP AGREEMENT

This Partnership Agreement (the "Agreement") is entered into as of [DATE] by and between [PARTNER A] and [PARTNER B].

1. Formation
The partners hereby form a partnership under the name [PARTNERSHIP NAME].

2. Capital Contributions
Each partner shall contribute the following: [CONTRIBUTIONS]

3. Profit and Loss Sharing
Partners shall share profits and losses as follows: [TERMS]`
    },
    {
        id: 7,
        name: 'Consulting Agreement',
        description: 'Professional consulting services template',
        icon: '💡',
        content: `CONSULTING AGREEMENT

This Consulting Agreement (the "Agreement") is entered into as of [DATE] by and between [CONSULTANT] and [CLIENT].

1. Services
Consultant shall provide the following consulting services: [SERVICES]

2. Compensation
Client shall pay Consultant [RATE] per [PERIOD], plus approved expenses.

3. Term
This Agreement shall commence on [START DATE] and continue until [END DATE].`
    },
    {
        id: 8,
        name: 'Software License',
        description: 'Software licensing and usage agreement',
        icon: '💻',
        content: `SOFTWARE LICENSE AGREEMENT

This Software License Agreement (the "Agreement") is entered into as of [DATE] by and between [LICENSOR] and [LICENSEE].

1. License Grant
Licensor grants Licensee a [TYPE] license to use the software known as [SOFTWARE NAME].

2. Restrictions
Licensee shall not: [RESTRICTIONS]

3. Term
This license shall be effective for [DURATION] from the effective date.`
    }
];

// React Components
function App() {
    const [selectedTemplate, setSelectedTemplate] = React.useState(null);
    const [riskAnalysis, setRiskAnalysis] = React.useState(null);
    const [isAnalyzing, setIsAnalyzing] = React.useState(false);
    const [error, setError] = React.useState(null);
    const [showInviteModal, setShowInviteModal] = React.useState(false);
    const [showRiskAnalysis, setShowRiskAnalysis] = React.useState(false);
    const [customContent, setCustomContent] = React.useState('');
    const [showCustomModal, setShowCustomModal] = React.useState(false);

    function openHelpModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-2xl font-bold text-gray-900">Help & Documentation</h3>
                    <button onclick="this.closest('.fixed').remove()" 
                        class="text-gray-500 hover:text-gray-700">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>

                <div class="space-y-8 text-gray-600">
                    <!-- Getting Started -->
                    <section>
                        <h4 class="text-xl font-semibold text-gray-800 mb-3">Getting Started</h4>
                        <div class="space-y-3">
                            <p>ContractIQ is your intelligent contract management solution that helps you create, analyze, and manage contracts efficiently.</p>
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <p class="font-medium text-blue-800">Quick Start:</p>
                                <ol class="list-decimal ml-4 mt-2 space-y-2 text-blue-700">
                                    <li>Choose a contract template or upload your own</li>
                                    <li>Customize the contract content</li>
                                    <li>Use AI analysis for risk assessment</li>
                                    <li>Send for signatures via DocuSign</li>
                                </ol>
                            </div>
                        </div>
                    </section>

                    <!-- Features -->
                    <section>
                        <h4 class="text-xl font-semibold text-gray-800 mb-3">Features</h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="p-4 border rounded-lg">
                                <h5 class="font-medium text-gray-800 mb-2">📝 Contract Templates</h5>
                                <ul class="list-disc ml-4 space-y-1">
                                    <li>Pre-built professional templates</li>
                                    <li>Custom contract upload</li>
                                    <li>Template customization</li>
                                    <li>Save custom templates</li>
                                </ul>
                            </div>
                            <div class="p-4 border rounded-lg">
                                <h5 class="font-medium text-gray-800 mb-2">🤖 AI Analysis</h5>
                                <ul class="list-disc ml-4 space-y-1">
                                    <li>Risk assessment</li>
                                    <li>Legal clause analysis</li>
                                    <li>Language improvement suggestions</li>
                                    <li>Compliance checking</li>
                                </ul>
                            </div>
                            <div class="p-4 border rounded-lg">
                                <h5 class="font-medium text-gray-800 mb-2">✍️ DocuSign Integration</h5>
                                <ul class="list-disc ml-4 space-y-1">
                                    <li>Electronic signatures</li>
                                    <li>Automatic field placement</li>
                                    <li>Multi-party signing</li>
                                    <li>Status tracking</li>
                                </ul>
                            </div>
                            <div class="p-4 border rounded-lg">
                                <h5 class="font-medium text-gray-800 mb-2">👥 Collaboration</h5>
                                <ul class="list-disc ml-4 space-y-1">
                                    <li>Invite team members</li>
                                    <li>Comment on contracts</li>
                                    <li>Version history</li>
                                    <li>Change tracking</li>
                                </ul>
                            </div>
                        </div>
                    </section>

                    <!-- Settings Guide -->
                    <section>
                        <h4 class="text-xl font-semibold text-gray-800 mb-3">Settings Configuration</h4>
                        <div class="space-y-4">
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <h5 class="font-medium text-gray-800 mb-2">API Keys Setup</h5>
                                <p class="mb-2">Configure your own API keys for enhanced functionality:</p>
                                <ul class="list-disc ml-4 space-y-2">
                                    <li>
                                        <span class="font-medium">OpenAI API Key:</span>
                                        <ul class="list-circle ml-4 mt-1">
                                            <li>Required for AI analysis features</li>
                                            <li>Get your key from <a href="https://platform.openai.com/api-keys" target="_blank" class="text-blue-600 hover:underline">OpenAI Dashboard</a></li>
                                        </ul>
                                    </li>
                                    <li>
                                        <span class="font-medium">DocuSign Integration Key:</span>
                                        <ul class="list-circle ml-4 mt-1">
                                            <li>Required for electronic signatures</li>
                                            <li>Available in your <a href="https://admin.docusign.com/api-integrator-key" target="_blank" class="text-blue-600 hover:underline">DocuSign Admin</a></li>
                                        </ul>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </section>

                    <!-- How-To Guides -->
                    <section>
                        <h4 class="text-xl font-semibold text-gray-800 mb-3">How-To Guides</h4>
                        <div class="space-y-4">
                            <div class="border-l-4 border-green-500 pl-4">
                                <h5 class="font-medium text-gray-800 mb-2">Creating a New Contract</h5>
                                <ol class="list-decimal ml-4 space-y-2">
                                    <li>Select a template or choose "Custom Contract"</li>
                                    <li>Fill in the required fields and customize content</li>
                                    <li>Click "Analyze" for AI-powered suggestions</li>
                                    <li>Review and make necessary changes</li>
                                    <li>Click "Send for Signature" when ready</li>
                                </ol>
                            </div>
                            <div class="border-l-4 border-blue-500 pl-4">
                                <h5 class="font-medium text-gray-800 mb-2">Collaborating with Team</h5>
                                <ol class="list-decimal ml-4 space-y-2">
                                    <li>Open the contract you want to share</li>
                                    <li>Click "Invite Collaborator" button</li>
                                    <li>Enter collaborator's email</li>
                                    <li>Set permissions and send invitation</li>
                                    <li>Track changes and comments in real-time</li>
                                </ol>
                            </div>
                            <div class="border-l-4 border-purple-500 pl-4">
                                <h5 class="font-medium text-gray-800 mb-2">Using AI Analysis</h5>
                                <ol class="list-decimal ml-4 space-y-2">
                                    <li>Select or upload your contract</li>
                                    <li>Click the "Analyze" button</li>
                                    <li>Review risk assessment and suggestions</li>
                                    <li>Apply recommended changes as needed</li>
                                    <li>Generate improved versions with AI assistance</li>
                                </ol>
                            </div>
                        </div>
                    </section>

                    <!-- Support -->
                    <section>
                        <h4 class="text-xl font-semibold text-gray-800 mb-3">Support</h4>
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <p class="mb-4">Need additional help? Our support team is here for you:</p>
                            <ul class="space-y-2">
                                <li>📧 Email: <a href="mailto:support@contractiq.ai" class="text-blue-600 hover:underline">support@contractiq.ai</a></li>
                                <li>📚 Documentation: <a href="https://docs.contractiq.ai" target="_blank" class="text-blue-600 hover:underline">docs.contractiq.ai</a></li>
                                <li>💬 Live Chat: Available in bottom-right corner during business hours</li>
                            </ul>
                        </div>
                    </section>
                </div>

                <div class="mt-6 flex justify-end">
                    <button onclick="this.closest('.fixed').remove()" 
                        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Close
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    function openSettingsModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <h3 class="text-xl font-bold mb-4 text-gray-900">Settings</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">API Configuration</label>
                        <div class="space-y-2">
                            <div>
                                <label class="block text-sm text-gray-600">OpenAI API Key</label>
                                <input type="password" id="openaiKey" class="w-full p-2 border rounded-lg">
                            </div>
                            <div>
                                <label class="block text-sm text-gray-600">DocuSign Integration Key</label>
                                <input type="password" id="docusignKey" class="w-full p-2 border rounded-lg">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-6 flex justify-end space-x-3">
                    <button onclick="this.closest('.fixed').remove()" 
                        class="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
                    <button onclick="saveSettings(this)" 
                        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Save</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Function to save settings
    window.saveSettings = async function(button) {
        const modal = button.closest('.fixed');
        const openaiKey = modal.querySelector('#openaiKey').value;
        const docusignKey = modal.querySelector('#docusignKey').value;

        try {
            const response = await fetch(`${API_BASE_URL}/api/settings/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    openaiKey,
                    docusignKey
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                alert('Settings saved successfully!');
                modal.remove();
            } else {
                alert('Error saving settings: ' + data.message);
            }
        } catch (error) {
            alert('Error saving settings: ' + error.message);
        }
    };

    // Custom Template Card Component
    const CustomTemplateCard = ({ onClick }) => {
        return e('div', {
            className: 'bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 cursor-pointer text-white',
            onClick: onClick
        },
            e('div', { className: 'flex items-start space-x-4' },
                e('div', { className: 'text-3xl' }, '📝'),
                e('div', { className: 'flex-1' },
                    e('h3', { className: 'text-lg font-semibold mb-1' }, 'Custom Contract'),
                    e('p', { className: 'text-sm opacity-90' }, 'Upload or paste your own contract')
                )
            )
        );
    };

    // Custom Contract Modal
    const CustomContractModal = ({ isOpen, onClose }) => {
        if (!isOpen) return null;

        const handleFileUpload = async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            try {
                const formData = new FormData();
                formData.append('file', file);

                setIsAnalyzing(true); // Show loading state while processing
                const response = await fetch(`${API_BASE_URL}/api/upload`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Upload failed');
                }

                const result = await response.json();
                if (result.content) {
                    setCustomContent(result.content);
                    onClose();
                    handleCustomTemplate(result.content);
                } else {
                    throw new Error('No content returned');
                }
            } catch (err) {
                console.error('Upload error:', err);
                setError('Failed to process file. Please try a different format or paste the content directly.');
            } finally {
                setIsAnalyzing(false);
            }
        };

        const handlePaste = () => {
            const content = document.getElementById('pasteArea').value;
            if (content) {
                setCustomContent(content);
                onClose();
                handleCustomTemplate(content);
            }
        };

        const handleDragOver = (e) => {
            e.preventDefault();
            e.stopPropagation();
        };

        const handleDrop = (e) => {
            e.preventDefault();
            e.stopPropagation();
            const files = e.dataTransfer.files;
            if (files.length) {
                const input = document.querySelector('input[type="file"]');
                input.files = files;
                handleFileUpload({ target: input });
            }
        };

        return e('div', {
            className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50',
            onClick: onClose
        },
            e('div', {
                className: 'bg-white rounded-lg p-6 max-w-2xl w-full mx-4',
                onClick: e => e.stopPropagation()
            },
                e('div', { className: 'flex justify-between items-center mb-6' },
                    e('h2', { className: 'text-2xl font-bold' }, 'Add Custom Contract'),
                    e('button', {
                        className: 'text-gray-500 hover:text-gray-700 text-2xl',
                        onClick: onClose
                    }, '×')
                ),
                e('div', { className: 'space-y-6' },
                    // File Upload with Drag & Drop
                    e('div', {
                        className: 'border-2 border-dashed border-gray-300 rounded-lg p-8 text-center space-y-4 hover:border-blue-500 transition-colors',
                        onDragOver: handleDragOver,
                        onDrop: handleDrop
                    },
                        e('div', { className: 'text-6xl mb-4' }, '📄'),
                        e('p', { className: 'text-gray-600' }, 'Drag and drop your contract file here'),
                        e('p', { className: 'text-sm text-gray-500' }, 'or'),
                        e('input', {
                            type: 'file',
                            accept: '.txt,.doc,.docx,.pdf',
                            onChange: handleFileUpload,
                            className: 'hidden',
                            id: 'fileInput'
                        }),
                        e('button', {
                            className: 'bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg inline-flex items-center space-x-2',
                            onClick: () => document.getElementById('fileInput').click()
                        },
                            e('span', { className: 'text-xl' }, '📎'),
                            e('span', null, 'Choose File')
                        ),
                        e('p', { className: 'text-xs text-gray-500 mt-2' }, 'Supports PDF (including compressed), DOC, DOCX, and TXT files')
                    ),
                    // Or Divider
                    e('div', { className: 'flex items-center' },
                        e('div', { className: 'flex-1 border-t' }),
                        e('div', { className: 'px-4 text-gray-500' }, 'OR'),
                        e('div', { className: 'flex-1 border-t' })
                    ),
                    // Paste Area
                    e('div', { className: 'space-y-2' },
                        e('label', { className: 'block font-medium' }, 'Paste Contract Text'),
                        e('textarea', {
                            id: 'pasteArea',
                            className: 'w-full h-48 p-2 border rounded',
                            placeholder: 'Paste your contract text here...'
                        }),
                        e('button', {
                            className: 'w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded flex items-center justify-center space-x-2',
                            onClick: handlePaste
                        },
                            e('span', { className: 'text-xl' }, '📋'),
                            e('span', null, 'Use Pasted Text')
                        )
                    )
                ),
                error && e('div', {
                    className: 'mt-4 p-4 bg-red-50 text-red-700 rounded-lg'
                }, error)
            )
        );
    };

    // Handle custom template
    const handleCustomTemplate = (content) => {
        const customTemplate = {
            id: 'custom-' + Date.now(),
            name: 'Custom Contract',
            description: 'Your uploaded or pasted contract',
            icon: '📝',
            content: content
        };
        setSelectedTemplate(customTemplate);
        setRiskAnalysis(null);
        setError(null);
        setShowRiskAnalysis(false);
    };

    // Template Card Component
    const TemplateCard = ({ template, onSelect, isSelected }) => {
        return e('div', {
            className: `bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 cursor-pointer ${isSelected ? 'ring-2 ring-blue-500' : ''}`,
            onClick: () => onSelect(template)
        },
            e('div', { className: 'flex items-start space-x-4' },
                e('div', { className: 'text-3xl' }, template.icon),
                e('div', { className: 'flex-1' },
                    e('h3', { className: 'text-lg font-semibold text-gray-900 mb-1' }, template.name),
                    e('p', { className: 'text-gray-600 text-sm' }, template.description)
                )
            )
        );
    };

    // Handle template selection
    const handleTemplateSelect = async (template) => {
        console.log('Template selected:', template);
        setSelectedTemplate(template);
        setRiskAnalysis(null);
        setError(null);
        setShowRiskAnalysis(false);
    };

    // Handle contract analysis
    async function handleContractAnalysis(content) {
        try {
            setIsAnalyzing(true);
            const response = await fetch(`${API_BASE_URL}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const result = await response.json();
            console.log('Contract analysis response:', result); // Debug log
            displayContractAnalysis(result);
        } catch (err) {
            console.error('Analysis error:', err);
            alert(err.message || 'Failed to analyze contract');
        } finally {
            setIsAnalyzing(false);
        }
    }

    // Handle risk analysis
    async function handleRiskAnalysis(content) {
        try {
            setIsAnalyzing(true);
            const response = await fetch(`${API_BASE_URL}/api/analyze/risks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error('Risk analysis failed');
            }

            const result = await response.json();
            displayRiskAnalysis(result);
        } catch (err) {
            console.error('Risk analysis error:', err);
            alert(err.message || 'Failed to analyze risks');
        } finally {
            setIsAnalyzing(false);
        }
    }

    // Display contract analysis results
    function displayContractAnalysis(analysis) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };

        const content = document.createElement('div');
        content.className = 'bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto';
        
        const analysisContent = analysis.sections && analysis.sections.length > 0 
            ? analysis.sections.map(section => `
                <div class="mb-6">
                    <h2 class="text-xl font-semibold mb-4">${section.title}</h2>
                    <div class="space-y-4">
                        ${section.items ? section.items.map(item => `
                            <div class="ml-4">
                                <div class="text-blue-600">${item.title}</div>
                                ${item.description ? `<div class="text-gray-700 ml-4">${item.description}</div>` : ''}
                            </div>
                        `).join('') : ''}
                    </div>
                </div>
            `).join('')
            : '<p>No analysis sections found.</p>';

        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-2xl font-bold">Contract Analysis</h1>
                    <button class="text-gray-500 hover:text-gray-700" onclick="this.closest('.fixed').remove()">×</button>
                </div>
                ${analysisContent}
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);
    }

    // Display risk analysis results
    function displayRiskAnalysis(analysis) {
        if (!analysis) {
            alert('No analysis results received');
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };

        const content = document.createElement('div');
        content.className = 'bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto';
        
        const concerns = analysis.concerns || [];
        
        content.innerHTML = `
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-3">
                        <img src="static/images/logo.png" alt="Logo" class="h-8 w-8">
                        <h1 class="text-2xl font-bold">Risk Analysis Report</h1>
                    </div>
                    <button class="text-gray-500 hover:text-gray-700" onclick="this.closest('.fixed').remove()">×</button>
                </div>
                
                <div class="mb-6">
                    <div class="flex items-center space-x-3">
                        <h2 class="text-xl">Overall Risk Score:</h2>
                        <span class="px-3 py-1 bg-green-500 text-white rounded-full">${analysis.risk_score || 'N/A'}/10</span>
                    </div>
                    <p class="mt-2 text-gray-700">${analysis.summary || 'No summary available.'}</p>
                </div>

                <div class="space-y-6">
                    <h2 class="text-xl font-semibold">Clause Analysis</h2>
                    ${concerns.length > 0 ? concerns.map(concern => `
                        <div class="p-4 rounded-lg ${getRiskLevelClass(concern.level)}">
                            <div class="flex justify-between items-center mb-2">
                                <h3 class="font-semibold">${concern.title || ''}</h3>
                                <span class="px-2 py-1 rounded text-sm ${getRiskLevelTextClass(concern.level)}">${concern.level || 'UNKNOWN'}</span>
                            </div>
                            <p>${concern.description || ''}</p>
                        </div>
                    `).join('') : '<p>No concerns found.</p>'}
                </div>
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);
    }

    // Helper function for risk level styling
    function getRiskLevelClass(level) {
        if (!level) return 'bg-gray-50';
        switch (level.toUpperCase()) {
            case 'HIGH': return 'bg-red-50';
            case 'MEDIUM': return 'bg-yellow-50';
            case 'LOW': return 'bg-green-50';
            default: return 'bg-gray-50';
        }
    }

    function getRiskLevelTextClass(level) {
        if (!level) return 'bg-gray-100 text-gray-800';
        switch (level.toUpperCase()) {
            case 'HIGH': return 'bg-red-100 text-red-800';
            case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
            case 'LOW': return 'bg-green-100 text-green-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }

    // Format analysis results helper
    function formatAnalysisResults(analysis) {
        return `
            <div class="space-y-6">
                ${analysis.sections ? analysis.sections.map(section => `
                    <div class="mb-6">
                        <h2 class="text-xl font-semibold mb-4">${section.title}</h2>
                        <div class="space-y-4">
                            ${section.items.map(item => `
                                <div class="ml-4">
                                    <div class="text-blue-600">${item.title}</div>
                                    ${item.description ? `<div class="text-gray-700 ml-4">${item.description}</div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('') : ''}
            </div>
        `;
    }

    // Make functions globally available
    window.openRewriteModal = function() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
                <h3 class="text-xl font-bold mb-4">Rewrite Contract</h3>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        Choose a rewrite option:
                    </label>
                    <div class="space-y-2">
                        <button onclick="window.handleRewrite('Make it more concise')" 
                            class="w-full text-left px-4 py-2 rounded hover:bg-gray-100">
                            Make it more concise
                        </button>
                        <button onclick="window.handleRewrite('Make it more formal')" 
                            class="w-full text-left px-4 py-2 rounded hover:bg-gray-100">
                            Make it more formal
                        </button>
                        <button onclick="window.handleRewrite('Add more protection clauses')" 
                            class="w-full text-left px-4 py-2 rounded hover:bg-gray-100">
                            Add more protection clauses
                        </button>
                        <button onclick="window.handleRewrite('Simplify language')" 
                            class="w-full text-left px-4 py-2 rounded hover:bg-gray-100">
                            Simplify language
                        </button>
                    </div>
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        Or provide custom instructions:
                    </label>
                    <textarea id="rewriteInstructions" 
                        class="w-full h-24 p-2 border rounded-lg" 
                        rows="4"
                        placeholder="Enter your specific requirements for the rewrite..."></textarea>
                </div>
                <div class="flex justify-end space-x-4">
                    <button onclick="this.closest('.fixed').remove()" 
                        class="px-4 py-2 text-gray-600 hover:text-gray-800">
                        Cancel
                    </button>
                    <button onclick="window.handleRewrite(document.getElementById('rewriteInstructions').value)" 
                        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Rewrite
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    };

    // Make rewrite handler globally available
    window.handleRewrite = async function(instructions) {
        if (!instructions || !instructions.trim()) {
            alert('Please provide rewrite instructions');
            return;
        }

        const textarea = document.getElementById('contractContent');
        if (!textarea || !textarea.value.trim()) {
            alert('Please enter contract content first');
            return;
        }
        
        try {
            console.log('Sending rewrite request:', {
                instructions: instructions.trim(),
                contentLength: textarea.value.trim().length
            });

            const response = await fetch(`${API_BASE_URL}/api/rewrite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: textarea.value.trim(),
                    instructions: instructions.trim()
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Rewrite failed');
            }
            
            const result = await response.json();
            console.log('Rewrite response:', result);

            if (!result || !result.rewritten) {
                throw new Error('No rewritten text received');
            }

            textarea.value = result.rewritten;
            
            // Close the modal if it exists
            const modal = document.querySelector('.fixed');
            if (modal) modal.remove();
            
        } catch (err) {
            console.error('Rewrite error:', err);
            alert(`Failed to rewrite contract: ${err.message}`);
        }
    };

    // Handle send signature button click
    window.openSignatureModal = function() {
        // Show signature options modal
        const signatureModal = document.createElement('div');
        signatureModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        signatureModal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
                <h3 class="text-xl font-bold mb-4">Send for Signature</h3>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Recipient Email
                    </label>
                    <input type="email" id="recipientEmail" class="w-full p-2 border rounded-lg" 
                        placeholder="Enter recipient's email...">
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Message (optional)
                    </label>
                    <textarea id="signatureMessage" class="w-full h-24 p-2 border rounded-lg" 
                        placeholder="Add a message to the recipient..."></textarea>
                </div>
                <div class="flex justify-end space-x-3">
                    <button onclick="this.closest('.fixed').remove()" 
                        class="px-4 py-2 text-gray-600 hover:text-gray-800">
                        Cancel
                    </button>
                    <button onclick="window.submitSignature()" 
                        class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
                        Send
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(signatureModal);
    };

    // Submit signature request
    window.submitSignature = async function() {
        const sendButton = document.querySelector('[onclick="window.submitSignature()"]');
        if (sendButton.disabled) return; // Prevent multiple submissions
        
        const email = document.getElementById('recipientEmail').value;
        const message = document.getElementById('signatureMessage').value;
        const textarea = document.getElementById('contractContent');
        
        if (!email || !textarea || !textarea.value.trim()) {
            alert('Please provide both recipient email and contract content');
            return;
        }
        
        try {
            // Disable the button and show loading state
            sendButton.disabled = true;
            sendButton.innerHTML = 'Sending...';
            
            const response = await fetch(`${API_BASE_URL}/api/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contract: textarea.value.trim(), // Changed from text to contract
                    signers: [{ email: email, name: email.split('@')[0] }],
                    use_ai_positioning: true
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to send signature request');
            }
            
            const result = await response.json();
            
            // Close the modal
            document.querySelector('.fixed').remove();
            alert('Contract sent for signature successfully!');
            
        } catch (err) {
            console.error('Signature error:', err);
            alert(err.message || 'Failed to send signature request');
            
            // Re-enable the button on error
            sendButton.disabled = false;
            sendButton.innerHTML = 'Send';
        }
    };

    // Format contract text for display
    function formatContractText(text) {
        // Remove excessive newlines while preserving paragraph breaks
        let formatted = text
            .replace(/\r\n/g, '\n') // Normalize line endings
            .replace(/\n{3,}/g, '\n\n') // Replace multiple newlines with double newline
            .replace(/([^\n])\n([^\n])/g, '$1 $2'); // Join single-line breaks with space
        
        return formatted;
    }

    // Update contract display
    function updateContractDisplay(newText) {
        const contractDisplay = document.getElementById('contractContent');
        if (contractDisplay) {
            contractDisplay.value = formatContractText(newText);
        }
    }

    // Handle file upload
    async function handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE_URL}/api/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Upload failed');

            const result = await response.json();
            if (result.content) {
                // Format the content before displaying
                updateContractDisplay(result.content);
            }
        } catch (err) {
            console.error('Upload error:', err);
            alert('Failed to upload file');
        }
    }

    // Main render
    return e('div', { className: 'min-h-screen bg-gradient-to-br from-blue-900 to-cyan-600' },
        // Header
        e('header', { className: 'bg-gradient-to-r from-blue-900 to-cyan-600 text-white py-4 px-6 shadow-lg' },
            e('div', { className: 'container mx-auto flex justify-between items-center' },
                e('div', { className: 'flex items-center space-x-2' },
                    e('h1', { className: 'text-2xl font-bold' }, 'ContractIQ'),
                    e('span', { className: 'text-sm opacity-75' }, 'Intelligent Contract Management')
                ),
                e('div', { className: 'flex items-center space-x-4' },
                    e('button', {
                        className: 'text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-white/10 transition-colors',
                        onClick: openHelpModal
                    }, '❓ Help'),
                    e('button', {
                        className: 'text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-white/10 transition-colors',
                        onClick: openSettingsModal
                    }, '⚙️ Settings'),
                    e('button', {
                        className: 'bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg transition-colors',
                        onClick: () => setShowInviteModal(true)
                    }, 'Invite Collaborator')
                )
            )
        ),

        // Main Content
        e('main', { className: 'container mx-auto px-6 py-8' },
            selectedTemplate
                ? e('div', { className: 'bg-white rounded-lg shadow-lg p-6' },
                    // Selected template view
                    e('div', { className: 'flex justify-between items-center mb-6' },
                        e('h2', { className: 'text-2xl font-bold text-gray-900' }, selectedTemplate.name),
                        e('button', {
                            className: 'text-blue-600 hover:text-blue-800 flex items-center space-x-2',
                            onClick: () => setSelectedTemplate(null)
                        },
                            e('span', null, '←'),
                            e('span', null, 'Back to Templates')
                        )
                    ),
                    e('div', { className: 'mt-6' },
                        e('textarea', {
                            id: 'contractContent',
                            className: 'w-full h-96 p-4 border rounded-lg font-mono text-sm',
                            value: selectedTemplate ? selectedTemplate.content : '',
                            onChange: (e) => {
                                setSelectedTemplate({
                                    ...selectedTemplate,
                                    content: e.target.value
                                });
                            },
                            placeholder: 'Select a template or paste your contract here...'
                        }),
                        e('div', { className: 'mt-4 flex space-x-4' },
                            e('button', {
                                className: 'px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center space-x-2',
                                onClick: () => handleContractAnalysis(selectedTemplate?.content || '')
                            },
                                e('span', { className: 'text-xl' }, '🔍'),
                                e('span', null, 'Analyze Contract')
                            ),
                            e('button', {
                                className: 'px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center space-x-2',
                                onClick: () => handleRiskAnalysis(selectedTemplate?.content || '')
                            },
                                e('span', { className: 'text-xl' }, '⚠️'),
                                e('span', null, 'Analyze Risk')
                            ),
                            e('button', {
                                className: 'px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center space-x-2',
                                onClick: () => window.openRewriteModal()
                            },
                                e('span', { className: 'text-xl' }, '✍️'),
                                e('span', null, 'Rewrite')
                            ),
                            e('button', {
                                className: 'px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center space-x-2',
                                onClick: () => window.openSignatureModal()
                            },
                                e('span', { className: 'text-xl' }, '✉️'),
                                e('span', null, 'Send for Signature')
                            )
                        )
                    ),
                )
                : e('div', null,
                    e('h2', { className: 'text-3xl font-bold text-white mb-8' }, 'Contract Templates'),
                    e('div', { className: 'grid gap-6 md:grid-cols-2 lg:grid-cols-3' },
                        // Custom Template Card
                        e(CustomTemplateCard, {
                            onClick: () => setShowCustomModal(true)
                        }),
                        // Standard Templates
                        templates.map(template =>
                            e(TemplateCard, {
                                key: template.id,
                                template,
                                onSelect: handleTemplateSelect,
                                isSelected: selectedTemplate?.id === template.id
                            })
                        )
                    )
                )
        ),

        // Modals
        e(CustomContractModal, {
            isOpen: showCustomModal,
            onClose: () => setShowCustomModal(false)
        }),

        // Loading Overlay
        isAnalyzing && e('div', { 
            className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50' 
        },
            e('div', { className: 'bg-white rounded-lg p-6 text-center' },
                e('div', { className: 'animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4' }),
                e('p', { className: 'text-lg font-semibold' }, 'Analyzing your contract...')
            )
        )
    );
}

// Export App to window
window.App = App;

// Initialize the app
window.addEventListener('DOMContentLoaded', () => {
    const rootElement = document.getElementById('root');
    if (rootElement) {
        ReactDOM.render(e(App), rootElement);
    }
});
