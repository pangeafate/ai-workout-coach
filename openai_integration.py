# openai_integration.py
import os
import openai

# Set your API key from the environment variable (for production use)
openai.api_key = os.getenv("OPENAI_API_KEY")

def query_openai(prompt: str) -> str:
    # Check if we're running in development mode
    if os.getenv("FLASK_ENV", "production") == "development":
        # Return a dummy response for local testing
        return "This is a simulated workout suggestion for local testing."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or use "gpt-4" if available and desired
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Error calling OpenAI API:", e)
        return "Sorry, I couldn't process that prompt."
