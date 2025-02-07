# test_openai.py
from openai_integration import query_openai

def main():
    prompt = "Tell me a fun fact."
    result = query_openai(prompt)
    print("OpenAI result:")
    print(result)

if __name__ == "__main__":
    main()
