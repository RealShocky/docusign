const Comments = ({ contractId }) => {
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showResolved, setShowResolved] = useState(false);

    useEffect(() => {
        fetchComments();
    }, [contractId, showResolved]);

    const fetchComments = async () => {
        try {
            const response = await fetch(
                `/docusign/api/contracts/${contractId}/comments?include_resolved=${showResolved}`
            );
            const data = await response.json();
            setComments(data);
            setLoading(false);
        } catch (err) {
            setError('Failed to load comments');
            setLoading(false);
        }
    };

    const addComment = async () => {
        if (!newComment.trim()) return;
        
        try {
            const response = await fetch(`/docusign/api/contracts/${contractId}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: newComment
                })
            });
            
            const comment = await response.json();
            setComments([...comments, comment]);
            setNewComment('');
        } catch (err) {
            setError('Failed to add comment');
        }
    };

    const resolveComment = async (commentId) => {
        try {
            await fetch(`/docusign/api/contracts/${contractId}/comments/${commentId}/resolve`, {
                method: 'POST'
            });
            
            // Update comment in the list
            setComments(comments.map(c => 
                c.id === commentId ? { ...c, resolved: true } : c
            ));
        } catch (err) {
            setError('Failed to resolve comment');
        }
    };

    if (loading) return <div className="p-4">Loading comments...</div>;
    if (error) return <div className="p-4 text-red-600">{error}</div>;

    return (
        <div className="p-4">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Comments</h2>
                <label className="flex items-center">
                    <input
                        type="checkbox"
                        checked={showResolved}
                        onChange={(e) => setShowResolved(e.target.checked)}
                        className="mr-2"
                    />
                    Show Resolved
                </label>
            </div>
            
            {/* Comment List */}
            <div className="space-y-4 mb-4">
                {comments.map(comment => (
                    <div 
                        key={comment.id}
                        className={`p-4 border rounded ${comment.resolved ? 'bg-gray-50' : 'bg-white'}`}
                    >
                        <div className="flex justify-between items-start">
                            <div>
                                <span className="font-medium">{comment.user.name}</span>
                                <span className="text-gray-500 text-sm ml-2">
                                    {new Date(comment.created_at).toLocaleString()}
                                </span>
                            </div>
                            {!comment.resolved && (
                                <button
                                    onClick={() => resolveComment(comment.id)}
                                    className="text-green-600 text-sm hover:text-green-700"
                                >
                                    Resolve
                                </button>
                            )}
                        </div>
                        <p className="mt-2">{comment.content}</p>
                        {comment.resolved && (
                            <span className="mt-2 inline-block px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                                Resolved
                            </span>
                        )}
                    </div>
                ))}
            </div>
            
            {/* New Comment Form */}
            <div className="flex gap-2">
                <input
                    type="text"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Add a comment..."
                    className="flex-1 p-2 border rounded"
                />
                <button
                    onClick={addComment}
                    disabled={!newComment.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                    Add
                </button>
            </div>
        </div>
    );
};
