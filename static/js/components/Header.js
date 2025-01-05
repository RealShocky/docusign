// Header Component
function Header({ onInviteClick }) {
    return React.createElement('nav', { className: 'gradient-bg text-white shadow-lg' },
        React.createElement('div', { className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8' },
            React.createElement('div', { className: 'flex justify-between h-16' },
                React.createElement('div', { className: 'flex items-center' },
                    React.createElement('img', { 
                        src: 'static/img/logo.png',
                        alt: 'ContractIQ Logo',
                        className: 'h-8 w-8 mr-2'
                    }),
                    React.createElement('span', { className: 'text-2xl font-bold' }, 'ContractIQ')
                ),
                React.createElement('div', { className: 'flex items-center' },
                    React.createElement('button', {
                        className: 'bg-white text-primary-600 px-4 py-2 rounded-md text-sm font-medium hover:bg-opacity-90 transition-colors',
                        onClick: onInviteClick
                    }, 'Invite Collaborators')
                )
            )
        )
    );
}

window.Header = Header;
