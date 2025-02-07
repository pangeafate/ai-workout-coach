# openai_integration.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set your API key from the environment variable.
# Make sure the environment variable is named "OPENAI_API_KEY"

def query_openai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",  # Or use "gpt-4" if available
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.7)
        # Access the response using dictionary syntax.
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling OpenAI API:", e)
        return "Sorry, I couldn't process that prompt."
