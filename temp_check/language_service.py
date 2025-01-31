import openai
import json
from typing import Dict, Any

class LanguageService:
    def __init__(self):
        pass

    def simplify_contract(self, contract_text: str) -> Dict[str, Any]:
        """Convert legal language to plain English"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": """You are a legal language simplification expert. 
                    Your task is to:
                    1. Break down complex legal terms into plain English
                    2. Maintain the legal meaning while making it understandable
                    3. Provide explanations for key terms
                    4. Keep the document structure intact

                    Return a JSON object with:
                    {
                        "simplified_text": "The full simplified contract",
                        "sections": [
                            {
                                "original": "Original section text",
                                "simplified": "Simplified version",
                                "key_terms": {
                                    "term": "explanation"
                                }
                            }
                        ],
                        "glossary": {
                            "legal_term": "simple explanation"
                        }
                    }"""},
                    {"role": "user", "content": f"Simplify this contract:\n\n{contract_text}"}
                ],
                temperature=0
            )
            
            simplified = json.loads(response.choices[0].message['content'])
            print("Contract simplification completed successfully")
            return simplified
            
        except Exception as e:
            print(f"Error in language simplification: {str(e)}")
            return {
                "error": f"Failed to simplify language: {str(e)}",
                "simplified_text": contract_text,
                "sections": [],
                "glossary": {}
            }

    def get_term_explanation(self, term: str) -> str:
        """Get a plain English explanation of a legal term"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are a legal terms expert. Explain legal terms in simple, plain English."},
                    {"role": "user", "content": f'Explain this legal term in simple English: "{term}"'}
                ],
                temperature=0
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error getting term explanation: {str(e)}")
            return f"Could not explain term: {term}"
