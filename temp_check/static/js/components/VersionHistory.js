const VersionHistory = ({ contractId }) => {
    const [versions, setVersions] = useState([]);
    const [selectedVersions, setSelectedVersions] = useState([]);
    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchVersions();
    }, [contractId]);

    const fetchVersions = async () => {
        try {
            const response = await fetch(`/docusign/api/contracts/${contractId}/versions`);
            const data = await response.json();
            setVersions(data);
            setLoading(false);
        } catch (err) {
            setError('Failed to load versions');
            setLoading(false);
        }
    };

    const compareVersions = async () => {
        if (selectedVersions.length !== 2) return;
        
        try {
            const [v1, v2] = selectedVersions;
            const response = await fetch(
                `/docusign/api/contracts/${contractId}/versions/compare?v1=${v1}&v2=${v2}`
            );
            const data = await response.json();
            setComparison(data);
        } catch (err) {
            setError('Failed to compare versions');
        }
    };

    const toggleVersionSelect = (version) => {
        if (selectedVersions.includes(version)) {
            setSelectedVersions(selectedVersions.filter(v => v !== version));
        } else if (selectedVersions.length < 2) {
            setSelectedVersions([...selectedVersions, version]);
        }
    };

    if (loading) return <div className="p-4">Loading version history...</div>;
    if (error) return <div className="p-4 text-red-600">{error}</div>;

    return (
        <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Version History</h2>
            
            {/* Version List */}
            <div className="space-y-2 mb-4">
                {versions.map(version => (
                    <div 
                        key={version.version}
                        className={`p-4 border rounded cursor-pointer ${
                            selectedVersions.includes(version.version) 
                                ? 'bg-blue-50 border-blue-500' 
                                : 'hover:bg-gray-50'
                        }`}
                        onClick={() => toggleVersionSelect(version.version)}
                    >
                        <div className="flex justify-between items-center">
                            <div>
                                <span className="font-medium">Version {version.version}</span>
                                <span className="text-gray-500 text-sm ml-2">
                                    {new Date(version.created_at).toLocaleString()}
                                </span>
                            </div>
                            <span className="text-sm">
                                by {version.created_by.name}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
            
            {/* Compare Button */}
            <button
                onClick={compareVersions}
                disabled={selectedVersions.length !== 2}
                className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
                Compare Selected Versions
            </button>
            
            {/* Comparison Results */}
            {comparison && (
                <div className="mt-4">
                    <h3 className="font-semibold mb-2">Comparison Results</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <h4 className="font-medium mb-2">
                                Version {comparison.version1.number}
                            </h4>
                            <pre className="p-4 bg-gray-50 rounded overflow-auto">
                                {comparison.version1.content}
                            </pre>
                        </div>
                        <div>
                            <h4 className="font-medium mb-2">
                                Version {comparison.version2.number}
                            </h4>
                            <pre className="p-4 bg-gray-50 rounded overflow-auto">
                                {comparison.version2.content}
                            </pre>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
