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
        return React.createElement('div', null, 'Loading collaborators...');
    }

    if (error) {
        return React.createElement('div', { className: 'error' }, error);
    }

    return React.createElement('div', { className: 'collaborators-list' },
        React.createElement('h3', null, 'Collaborators'),
        React.createElement('div', { className: 'invitations' },
            invitations.map(invitation => 
                React.createElement('div', { key: invitation.id, className: 'invitation-item' },
                    React.createElement('div', { className: 'invitation-email' }, invitation.email),
                    React.createElement('div', { className: 'invitation-role' }, `Role: ${invitation.role}`),
                    React.createElement('div', { className: 'invitation-status' }, 
                        `Status: ${invitation.status}`,
                        invitation.status === 'pending' && 
                        React.createElement('span', { className: 'expires' }, 
                            ` (Expires: ${new Date(invitation.expires_at).toLocaleDateString()})`
                        )
                    )
                )
            )
        )
    );
}

window.CollaboratorsList = CollaboratorsList;
