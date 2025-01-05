// Template Card Component
function TemplateCard({ template, onSelect }) {
    const e = React.createElement;
    return e('div', {
        className: 'bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-all cursor-pointer',
        onClick: () => onSelect(template)
    },
        e('div', { className: 'text-4xl mb-4' }, template.icon),
        e('h3', { className: 'text-lg font-semibold mb-2' }, template.name),
        e('p', { className: 'text-gray-600 text-sm' }, template.description)
    );
}
