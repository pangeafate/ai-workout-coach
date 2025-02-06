import subprocess

def query_llama(prompt: str) -> str:
    """
    Runs the Llama3.2 model via Ollama with the provided prompt and returns the output.
    The prompt is passed as a positional argument.
    """
    try:
        # Adjust the order of arguments if necessary
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt, "--verbose"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Error calling the Llama model:", e)
        print("stderr output:", e.stderr)
        return "Sorry, I couldn't process that prompt."
