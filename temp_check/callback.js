const { useState, useEffect } = React;

function Callback() {
    const [status, setStatus] = useState('Processing...');
    const [error, setError] = useState(null);

    useEffect(() => {
        const handleCallback = async () => {
            try {
                // Get the authorization code from URL
                const urlParams = new URLSearchParams(window.location.search);
                const code = urlParams.get('code');
                
                if (!code) {
                    throw new Error('No authorization code received');
                }

                // Get DocuSign configuration
                const configResponse = await fetch('http://localhost:5000/api/auth/docusign-config');
                const config = await configResponse.json();

                // Exchange code for token
                const tokenResponse = await fetch(config.tokenUri, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        'grant_type': 'authorization_code',
                        'code': code,
                        'client_id': config.clientId,
                        'redirect_uri': config.redirectUri
                    })
                });

                if (!tokenResponse.ok) {
                    throw new Error('Failed to get access token');
                }

                const tokenData = await tokenResponse.json();
                
                // Store the access token
                localStorage.setItem('docusign_access_token', tokenData.access_token);
                
                // Send the contract for signature
                const contract = localStorage.getItem('pending_contract');
                const signers = JSON.parse(localStorage.getItem('pending_signers') || '[]');
                
                if (contract && signers.length > 0) {
                    const response = await fetch('http://localhost:5000/api/contracts/send', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${tokenData.access_token}`
                        },
                        body: JSON.stringify({
                            contract: contract,
                            signers: signers
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Failed to send contract');
                    }

                    const result = await response.json();
                    setStatus('Contract sent successfully!');
                    
                    // Clear pending data
                    localStorage.removeItem('pending_contract');
                    localStorage.removeItem('pending_signers');
                    
                    // Redirect back to main page after 2 seconds
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                }
            } catch (err) {
                setError(err.message);
                setStatus('Failed');
            }
        };

        handleCallback();
    }, []);

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
                <h1 className="text-2xl font-bold mb-4">DocuSign Authorization</h1>
                
                {error ? (
                    <div className="bg-red-100 text-red-700 p-4 rounded-lg">
                        {error}
                    </div>
                ) : (
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                        <p className="text-gray-600">{status}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

ReactDOM.render(<Callback />, document.getElementById('root'));
