import json
import os
from openai import OpenAI
from typing import List, Dict, Any

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class RiskService:
    def __init__(self):
        self.risk_categories = {
            'high': {'color': 'red', 'description': 'High risk - requires immediate attention'},
            'medium': {'color': 'yellow', 'description': 'Medium risk - should be reviewed'},
            'low': {'color': 'green', 'description': 'Low risk - standard terms'}
        }
        self.risk_prompt = """
        Analyze the following contract for potential risks and issues. Consider:
        1. Legal compliance
        2. Financial risks
        3. Liability concerns
        4. Ambiguous language
        5. Missing clauses
        6. Unfavorable terms
        
        Provide a detailed analysis with:
        1. Overall risk score (1-10)
        2. Risk summary
        3. Specific clause analysis
        
        Contract:
        {contract_text}
        """

    def analyze_contract_risks(self, contract_text: str) -> Dict[str, Any]:
        """Analyze contract for potential risks using GPT"""
        try:
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4-1106-preview'),
                messages=[
                    {"role": "system", "content": "You are a legal expert analyzing contract risks."},
                    {"role": "user", "content": self.risk_prompt.format(contract_text=contract_text)}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            print("Risk analysis completed successfully")
            return analysis
            
        except Exception as e:
            print(f"Error in risk analysis: {str(e)}")
            return {
                "error": f"Failed to analyze risks: {str(e)}",
                "overall_risk_score": 0,
                "risk_summary": "Analysis failed",
                "clauses": [],
                "key_concerns": ["Analysis could not be completed"]
            }

    def get_risk_color(self, risk_level: str) -> str:
        """Get the color associated with a risk level"""
        return self.risk_categories.get(risk_level.lower(), {}).get('color', 'gray')

    def get_risk_description(self, risk_level: str) -> str:
        """Get the description associated with a risk level"""
        return self.risk_categories.get(risk_level.lower(), {}).get('description', 'Unknown risk level')
