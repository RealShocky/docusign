import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')

class AIService:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
    def analyze_contract(self, contract_text):
        """Analyze contract text and identify key terms and potential issues"""
        sentences = sent_tokenize(contract_text)
        analysis = {
            'key_terms': self._extract_key_terms(sentences),
            'suggestions': self._generate_suggestions(sentences),
            'risk_assessment': self._assess_risks(sentences)
        }
        return analysis
    
    def _extract_key_terms(self, sentences):
        """Extract key terms and definitions from contract"""
        key_terms = []
        for sentence in sentences:
            if "means" in sentence.lower() or "shall mean" in sentence.lower():
                key_terms.append(sentence)
        return key_terms
    
    def _generate_suggestions(self, sentences):
        """Generate revision suggestions based on best practices"""
        suggestions = []
        for sentence in sentences:
            # Example checks
            if len(sentence.split()) > 50:  # Complex sentence
                suggestions.append({
                    'original': sentence,
                    'suggestion': 'Consider breaking this sentence into smaller parts for clarity',
                    'type': 'readability'
                })
            if "shall" in sentence:  # Archaic language
                suggestions.append({
                    'original': sentence,
                    'suggestion': 'Consider using "must" or "will" instead of "shall"',
                    'type': 'modernization'
                })
        return suggestions
    
    def _assess_risks(self, sentences):
        """Assess potential risks in contract language"""
        risks = []
        risk_keywords = ['terminate', 'liability', 'indemnify', 'warrant']
        
        for sentence in sentences:
            for keyword in risk_keywords:
                if keyword in sentence.lower():
                    risks.append({
                        'sentence': sentence,
                        'risk_type': keyword,
                        'severity': 'medium'  # This could be made more sophisticated
                    })
        return risks
    
    def generate_revision(self, contract_text, suggestions):
        """Generate revised contract based on suggestions"""
        revised_text = contract_text
        for suggestion in suggestions:
            if suggestion.get('auto_apply', False):
                revised_text = revised_text.replace(
                    suggestion['original'],
                    suggestion['proposed_text']
                )
        return revised_text
