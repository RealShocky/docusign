function CollaboratorsList({ contractId }) {
    const [invitations, setInvitations] = React.useState([]);
    const [isLoading, setIsLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    const fetchInvitations = async () => {
        try {
            const response = await fetch(`/api/contracts/${contractId}/invitations`);
            if (!response.ok) {
                throw new Error('Failed to fetch invitations');
            }
            const data = await response.json();
            setInvitations(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    React.useEffect(() => {
        fetchInvitations();
    }, [contractId]);

    if (isLoading) {
        return e('div', null, 'Loading collaborators...');
    }

    if (error) {
        return e('div', { className: 'error' }, error);
    }

    return e('div', { className: 'collaborators-list' },
        e('h3', null, 'Collaborators'),
        e('div', { className: 'invitations' },
            invitations.map(invitation => 
                e('div', { key: invitation.id, className: 'invitation-item' },
                    e('div', { className: 'invitation-email' }, invitation.email),
                    e('div', { className: 'invitation-role' }, `Role: ${invitation.role}`),
                    e('div', { className: 'invitation-status' }, 
                        `Status: ${invitation.status}`,
                        invitation.status === 'pending' && 
                        e('span', { className: 'expires' }, 
                            ` (Expires: ${new Date(invitation.expires_at).toLocaleDateString()})`
                        )
                    )
                )
            )
        )
    );
}
