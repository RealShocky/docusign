// Header Component
const Header = ({ onInviteClick }) => {
    function openHelpModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
                <h3 class="text-xl font-bold mb-4 text-gray-900">Help & Documentation</h3>
                <div class="text-gray-600 space-y-4">
                    <div>
                        <h4 class="font-semibold text-gray-800">Getting Started</h4>
                        <p>ContractIQ helps you manage, analyze, and sign contracts efficiently. Here's how to get started:</p>
                        <ul class="list-disc ml-6 mt-2">
                            <li>Choose a template or create a custom contract</li>
                            <li>Use AI to analyze risks and improve contract language</li>
                            <li>Send contracts for signature using DocuSign integration</li>
                            <li>Collaborate with team members in real-time</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-800">Key Features</h4>
                        <ul class="list-disc ml-6">
                            <li>AI-powered contract analysis and risk assessment</li>
                            <li>Smart contract rewriting suggestions</li>
                            <li>Secure electronic signatures via DocuSign</li>
                            <li>Real-time collaboration tools</li>
                            <li>Template management system</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-800">Need More Help?</h4>
                        <p>Contact our support team at support@contractiq.ai</p>
                    </div>
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
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            API Configuration
                        </label>
                        <div class="space-y-2">
                            <div>
                                <label class="block text-sm text-gray-600">OpenAI API Key</label>
                                <input type="password" id="openaiKey" 
                                    class="w-full p-2 border rounded-lg" 
                                    placeholder="Enter OpenAI API key">
                            </div>
                            <div>
                                <label class="block text-sm text-gray-600">DocuSign Integration</label>
                                <input type="password" id="docusignKey" 
                                    class="w-full p-2 border rounded-lg" 
                                    placeholder="Enter DocuSign integration key">
                            </div>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Preferences
                        </label>
                        <div class="space-y-2">
                            <div class="flex items-center">
                                <input type="checkbox" id="autoAnalyze" 
                                    class="h-4 w-4 text-blue-600 rounded">
                                <label class="ml-2 text-sm text-gray-600">
                                    Auto-analyze new contracts
                                </label>
                            </div>
                            <div class="flex items-center">
                                <input type="checkbox" id="darkMode" 
                                    class="h-4 w-4 text-blue-600 rounded">
                                <label class="ml-2 text-sm text-gray-600">
                                    Enable dark mode
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-6 flex justify-end space-x-3">
                    <button onclick="this.closest('.fixed').remove()" 
                        class="px-4 py-2 text-gray-600 hover:text-gray-800">
                        Cancel
                    </button>
                    <button onclick="saveSettings()" 
                        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Save Changes
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    return e('header', { className: 'bg-gradient-to-r from-blue-900 to-cyan-600 text-white py-4 px-6 shadow-lg' },
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
                    onClick: onInviteClick
                }, 'Invite Collaborator')
            )
        )
    );
};

// Save settings function
window.saveSettings = function() {
    const openaiKey = document.getElementById('openaiKey').value;
    const docusignKey = document.getElementById('docusignKey').value;
    const autoAnalyze = document.getElementById('autoAnalyze').checked;
    const darkMode = document.getElementById('darkMode').checked;

    // Save settings to localStorage
    const settings = {
        openaiKey: openaiKey,
        docusignKey: docusignKey,
        autoAnalyze: autoAnalyze,
        darkMode: darkMode
    };
    localStorage.setItem('contractiq_settings', JSON.stringify(settings));

    // Close modal
    document.querySelector('.fixed').remove();
    alert('Settings saved successfully!');
};

// Make sure e is defined
const e = React.createElement;

// Export Header to window
window.Header = Header;
