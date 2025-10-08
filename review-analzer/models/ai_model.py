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
    try:
        json_str = response.content.strip()
        # Remove markdown or custom tags
        json_str = re.sub(r'```json|```|\[ASS\]|\[/ASS\]|\[INST\]|\[/INST\]', '', json_str)
        json_str = json_str.strip()
        return json.loads(json_str)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Invalid JSON response"}


# Define processing pipeline
chain = prompt | model | clean_json

def analyze_review(review_text):
    """Runs the AI model and returns structured output."""
    return chain.invoke({"review": review_text})
