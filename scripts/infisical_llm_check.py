import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from openai import OpenAI


def init_environment() -> None:
    """
    Initialize environment variables and load .env file.
    """
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    load_dotenv(override=True)


def get_llm_client():
    """
    Initialize and return an OpenAI client using Infisical to get the API key.
    """
    # Import after path is set up
    from expert_finder.infrastructure.settings.inf import get_secret

    env = os.environ.get("ENVIRONMENT", "staging")

    # Get API key from Infisical
    api_key = get_secret("OPENAI_KEY", env)

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    return client


def ask_llm_question(client: OpenAI, question: str, model: str = "gpt-4o-mini") -> str:
    """
    Ask a simple question to the LLM and return the answer.

    Args:
        client: OpenAI client instance
        question: The question to ask
        model: The model name to use (default: "gpt-4o-mini")

    Returns:
        The LLM's response as a string
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
    )

    if response.choices and len(response.choices) > 0:
        return response.choices[0].message.content
    else:
        return "No response received from the LLM."


def main() -> None:
    """
    Main function to test LLM connection with a sample question.
    """
    print("Initializing environment...")
    init_environment()

    print("Connecting to LLM via Infisical...")
    client = get_llm_client()

    # Simple sample question
    sample_question = "What is the capital of France? Please answer in one sentence."

    # Available OpenAI models you can use:
    # - "gpt-4o-mini" (default, fast and cost-effective)
    # - "gpt-4o" (more capable)
    # - "gpt-4-turbo" (high performance)
    # - "gpt-4" (standard GPT-4)
    # - "gpt-3.5-turbo" (older, cheaper option)
    #
    # You can set the model via environment variable:
    #   export LLM_MODEL="gpt-4o"
    # Or change the default below
    model_name = os.environ.get("LLM_MODEL", "gpt-4o")

    print(f"\nAsking question: {sample_question}")
    print(f"Using model: {model_name}")
    print("-" * 60)

    try:
        answer = ask_llm_question(client, sample_question, model=model_name)
        print(f"\nAnswer:\n{answer}")
        print("-" * 60)
        print("\n✅ Successfully connected to LLM!")
    except Exception as e:
        print(f"\n❌ Error connecting to LLM: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
