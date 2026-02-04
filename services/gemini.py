import os
import logging
from dotenv import load_dotenv
from google import genai

# Load env vars
load_dotenv()

# Create Gemini client (NEW SDK)
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_summary_stream(transcript_text: str, summary_language: str = "English"):
    """
    Streams a summary using Gemini 1.5 Flash (NEW API).
    """
    prompt = f"""
    Provide a clear, well-structured summary in {summary_language}.

    Transcript:
    {transcript_text}
    """

    try:
        stream = client.models.generate_content_stream(
            model="models/gemini-2.5-flash",
            contents=prompt,
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        logging.exception("Gemini streaming failed")
        yield f"Error generating summary: {e}"
