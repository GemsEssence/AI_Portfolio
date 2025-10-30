### AI Project Hub

### This repository contains multiple AI-powered applications and a central dashboard. All apps share a common Python virtual environment.

### Project Structure
```bash
ai-portfolio/
├── shared_venv/                    # Shared Python virtual environment
├── Personalized_Shopping_Recommendation/
├── review_analyzer/
├── ai_interview_app/
├── object_detect-info/
├── fashion_search_bot/
├── LegalMind/
├── ai-medi-bot/
├── run_all.sh                       # Master launcher script
├── ai_project_hub/                  # Dashboard project
├── requirements.txt                 # Single requirements file for all apps
└── README.md
```

### Setup Instructions

## 1. Clone the repository
```bash
git clone https://github.com/GemsEssence/AI_Portfolio.git
cd AI_Portfolio
```
### 2. Activate the shared virtual environment
```bash
source shared_venv/bin/activate
```

### If shared_venv does not exist, create it:
```bash
python -m venv shared_venv
source shared_venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Go to each app folder and create a .env file if required, following the folder’s README instructions.

### 5. Launch all apps
```bash
./run_all.sh
```