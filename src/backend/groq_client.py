import requests
from src.utils.config import load_config

class GroqClient:
    def __init__(self):
        self.config = load_config()
        self.api_key = self.config["GROQ_API_KEY"]
        self.model = self.config["GROQ_MODEL"]
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def ask(self, prompt):
        """Send a prompt to the Groq API and return the response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        response = requests.post(self.base_url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"[ERROR] Groq API failed: {response.status_code} - {response.text}")
            return "שגיאה: לא ניתן היה לקבל תשובה מהבינה המלאכותית."

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

# Create a singleton instance
groq_client = GroqClient() 