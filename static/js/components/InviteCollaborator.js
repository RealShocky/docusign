function InviteCollaborator({ contractId, onInviteSent }) {
    const [email, setEmail] = React.useState('');
    const [role, setRole] = React.useState('viewer');
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`/api/contracts/${contractId}/invitations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, role }),
            });

            if (!response.ok) {
                throw new Error('Failed to send invitation');
            }

            const data = await response.json();
            setEmail('');
            if (onInviteSent) {
                onInviteSent(data);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return React.createElement('div', { className: 'invite-collaborator' },
        React.createElement('h3', null, 'Invite Collaborator'),
        error && React.createElement('div', { className: 'error' }, error),
        React.createElement('form', { onSubmit: handleSubmit },
            React.createElement('div', { className: 'form-group' },
                React.createElement('label', null, 'Email:'),
                React.createElement('input', {
                    type: 'email',
                    value: email,
                    onChange: (e) => setEmail(e.target.value),
                    required: true,
                    disabled: isLoading,
                })
            ),
            React.createElement('div', { className: 'form-group' },
                React.createElement('label', null, 'Role:'),
                React.createElement('select', {
                    value: role,
                    onChange: (e) => setRole(e.target.value),
                    disabled: isLoading,
                },
                    React.createElement('option', { value: 'viewer' }, 'Viewer'),
                    React.createElement('option', { value: 'editor' }, 'Editor'),
                    React.createElement('option', { value: 'admin' }, 'Admin')
                )
            ),
            React.createElement('button', {
                type: 'submit',
                disabled: isLoading,
                className: 'btn btn-primary'
            }, isLoading ? 'Sending...' : 'Send Invitation')
        )
    );
}

window.InviteCollaborator = InviteCollaborator;
