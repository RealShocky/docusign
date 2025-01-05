import openai
import json
import os
from typing import List, Dict, Any

class RiskService:
    def __init__(self):
        self.risk_categories = {
            'high': {'color': 'red', 'description': 'High risk - requires immediate attention'},
            'medium': {'color': 'yellow', 'description': 'Medium risk - should be reviewed'},
            'low': {'color': 'green', 'description': 'Low risk - standard terms'}
        }

    def analyze_contract_risks(self, contract_text: str) -> Dict[str, Any]:
        """Analyze contract for potential risks using GPT"""
        try:
            model = os.getenv('OPENAI_MODEL', 'gpt-4-1106-preview')
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": """You are a legal risk analysis expert. Analyze the contract for potential risks and issues.
                    For each clause or section:
                    1. Identify potential risks
                    2. Assign a risk level (high, medium, low)
                    3. Provide specific explanations
                    4. Suggest improvements

                    Return a JSON object with:
                    {
                        "overall_risk_score": 1-10,
                        "risk_summary": "Brief summary",
                        "clauses": [
                            {
                                "text": "Clause text",
                                "risk_level": "high/medium/low",
                                "risk_factors": ["list of specific risks"],
                                "explanation": "Detailed explanation",
                                "suggestions": ["list of improvements"]
                            }
                        ],
                        "key_concerns": ["List of major concerns"]
                    }"""},
                    {"role": "user", "content": f"Analyze this contract for risks:\n\n{contract_text}"}
                ],
                temperature=0
            )
            
            analysis = json.loads(response.choices[0].message['content'])
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
