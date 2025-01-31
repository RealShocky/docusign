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

    return e('div', { className: 'invite-collaborator' },
        e('h3', null, 'Invite Collaborator'),
        error && e('div', { className: 'error' }, error),
        e('form', { onSubmit: handleSubmit },
            e('div', { className: 'form-group' },
                e('label', null, 'Email:'),
                e('input', {
                    type: 'email',
                    value: email,
                    onChange: (e) => setEmail(e.target.value),
                    required: true,
                    disabled: isLoading,
                })
            ),
            e('div', { className: 'form-group' },
                e('label', null, 'Role:'),
                e('select', {
                    value: role,
                    onChange: (e) => setRole(e.target.value),
                    disabled: isLoading,
                },
                    e('option', { value: 'viewer' }, 'Viewer'),
                    e('option', { value: 'editor' }, 'Editor'),
                    e('option', { value: 'admin' }, 'Admin')
                )
            ),
            e('button', {
                type: 'submit',
                disabled: isLoading,
                className: 'btn btn-primary'
            }, isLoading ? 'Sending...' : 'Send Invitation')
        )
    );
}
