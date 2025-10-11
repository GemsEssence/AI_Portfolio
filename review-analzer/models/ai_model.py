from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.prompts import ChatPromptTemplate
import json
import re

load_dotenv()

# Initialize Hugging Face LLM
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    max_new_tokens=300,
    temperature=0.8,
    top_p=0.95
)

# Chat model
model = ChatHuggingFace(llm=llm)

# Define prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a product review analyzer. Return ONLY valid JSON with:
    {{
        "summary": "concise 10-word summary",
        "sentiment": "POSITIVE/NEUTRAL/NEGATIVE"
    }}
    Do not add any extra text or explanations."""),

    ("human", "Review to analyze:\n{review}")
])

# Function to clean JSON output
def clean_json(response):
    """
    Robustly parse Hugging Face model output for review analysis.
    Always returns a dict with 'summary' and 'sentiment'.
    """
    default_output = {"summary": "", "sentiment": "NEUTRAL", "error": None}

    try:
        json_str = response.content.strip()

        # Debug: see raw response
        print(json_str, "RAW RESPONSE >>>")

        # Remove markdown and Hugging Face instruction tags
        json_str = re.sub(r'```json|```|\[ASS\]|\[/ASS\]|\[INST\]|\[/INST\]', '', json_str)
        json_str = json_str.strip()

        # Extract the first JSON object
        match = re.search(r'\{.*?\}', json_str, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            # Ensure required keys exist    
            parsed.setdefault("summary", "")
            parsed.setdefault("sentiment", "NEUTRAL")
            parsed.setdefault("error", None)
            return parsed
        else:
            default_output["error"] = "No valid JSON found in response"
            return default_output

    except json.JSONDecodeError as e:
        default_output["error"] = f"JSON decoding failed: {e}"
        return default_output


# Define processing pipeline    
chain = prompt | model | clean_json

def analyze_review(review_text):
    """Runs the AI model and returns structured output."""
    return chain.invoke({"review": review_text})
