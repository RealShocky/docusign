const TemplateList = ({ onSelectTemplate }) => {
    const [templates, setTemplates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedTags, setSelectedTags] = useState([]);

    useEffect(() => {
        fetchTemplates();
    }, [selectedCategory, selectedTags]);

    const fetchTemplates = async () => {
        try {
            let url = '/docusign/api/templates';
            const params = new URLSearchParams();
            
            if (selectedCategory !== 'all') {
                params.append('category', selectedCategory);
            }
            
            selectedTags.forEach(tag => params.append('tags', tag));
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            const response = await fetch(url);
            const data = await response.json();
            setTemplates(data);
            setLoading(false);
        } catch (err) {
            setError('Failed to load templates');
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4">Loading templates...</div>;
    if (error) return <div className="p-4 text-red-600">{error}</div>;

    return (
        <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Contract Templates</h2>
            
            {/* Category Filter */}
            <div className="mb-4">
                <select 
                    className="p-2 border rounded"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                >
                    <option value="all">All Categories</option>
                    <option value="service">Service Agreements</option>
                    <option value="employment">Employment Contracts</option>
                    <option value="nda">Non-Disclosure Agreements</option>
                    <option value="sale">Sales Contracts</option>
                </select>
            </div>
            
            {/* Template List */}
            <div className="grid gap-4">
                {templates.map(template => (
                    <div 
                        key={template.id}
                        className="p-4 border rounded hover:bg-gray-50 cursor-pointer"
                        onClick={() => onSelectTemplate(template)}
                    >
                        <h3 className="font-medium">{template.name}</h3>
                        <p className="text-sm text-gray-600">{template.description}</p>
                        <div className="mt-2 flex gap-2">
                            {template.tags.map(tag => (
                                <span 
                                    key={tag}
                                    className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                                >
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
