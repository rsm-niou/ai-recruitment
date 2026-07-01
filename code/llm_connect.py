import os
import requests
import google.generativeai as genai_legacy # Fallback or just keep for context if needed, but we'll try to mostly rely on new one if possible or just replace it.
# Actually, let's just do a clean replacement of imports as well to avoid confusion.

from google import genai
from google.genai import types
import markdown as markdown_lib
from typing import List, Optional, Callable, Union

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

# Default models
DEFAULT_LLAMA_MODEL = "meta-llama/Llama-3.2-1B-Instruct"
DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"

_gemini_client = None

def query_gemini(
    messages: List[dict],
    model: str = DEFAULT_GEMINI_MODEL,
    max_tokens: int = 4000,
    temperature: float = 0.4,
    api_key: Optional[str] = None,
) -> str:
    """
    Send a query to the Gemini API using the new google-genai SDK.
    """
    global _gemini_client
    
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini: API key is required")

    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=api_key)

    # Adapt OpenAI-style messages to Gemini format (single string prompt works best for simple queries)
    system_messages = [m["content"] for m in messages if m["role"] == "system"]
    user_messages = [m["content"] for m in messages if m["role"] == "user"]
    prompt = "\n\n".join(system_messages + user_messages)

    # Use the new SDK pattern
    # Note: 'thinking_config' is only available on some models/versions, 
    # checking user's example: types.GenerateContentConfig(thinking_config=...)
    # We will use standard config for broad compatibility unless model is specific.
    
    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    
    try:
        response = _gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {e}"

def query_hf(
    messages: List[dict],
    model: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.4,
    api_key: Optional[str] = None,
) -> str:
    """
    Send a query to Hugging Face via InferenceClient.
    """
    if InferenceClient is None:
        raise RuntimeError("huggingface_hub is not installed")

    api_key = api_key or os.getenv("HF_TOKEN")
    if not api_key:
        raise ValueError("HF: HF_TOKEN is required")

    model = model or os.getenv("HF_MODEL", DEFAULT_LLAMA_MODEL)

    client = InferenceClient(api_key=api_key)
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Common error handling
        if "404" in str(e):
             raise RuntimeError(f"HF Model '{model}' not found or not available.") from e
        raise e

def get_response(
    input: Union[str, List[str]],
    template: Optional[Callable] = None,
    role: str = "You are a helpful assistant.",
    temperature: float = 0.4,
    max_tokens: int = 4000,
    render_md: bool = True,
    md: Optional[bool] = None,
    llm: Optional[str] = None,
    model_name: Optional[str] = None,
) -> str:
    """
    Unified entry point for LLM responses.
    """
    # Backwards compatibility for 'md' argument
    if md is not None:
        render_md = md

    # Default template: join list or return string
    if template is None:
        def template(x):
            return "\n".join([str(i) for i in x]) if isinstance(x, list) else str(x)

    messages = [
        {"role": "system", "content": role},
        {"role": "user", "content": template(input)},
    ]

    response_text = ""

    # Resolve backend
    if llm == "gemini":
        response_text = query_gemini(
            messages=messages,
            model=model_name or DEFAULT_GEMINI_MODEL,
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif llm == "llama":
        # Specific path for 'llama' as requested by legacy code
        response_text = query_hf(
            messages=messages,
            model=DEFAULT_LLAMA_MODEL, # Enforce default llama model for this keyword
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif llm == "hf":
        response_text = query_hf(
            messages=messages,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        raise ValueError(f"LLM: Invalid or missing LLM provider specified: '{llm}'. Options: gemini, llama, hf")
    
    # Markdown rendering
    if render_md:
        try:
            return markdown_lib.markdown(response_text)
        except Exception:
            return response_text
    
    return response_text

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing get_response with HF...")
    try:
        res = get_response("Say hello", llm="hf", md=False)
        print("Result:", res)
    except Exception as e:
        print("Error:", e)
