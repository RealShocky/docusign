// Contract Templates Component
function ContractTemplates({ onSelectTemplate }) {
    const e = React.createElement;
    return e('div', { className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8' },
        e('h2', { className: 'text-2xl font-bold mb-6' }, 'Contract Templates'),
        e('div', { className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6' },
            contractTemplates.map(template =>
                e(TemplateCard, {
                    key: template.id,
                    template,
                    onSelect: onSelectTemplate
                })
            )
        )
    );
}
