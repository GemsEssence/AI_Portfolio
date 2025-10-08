#!/bin/bash
# ===============================================
# 🚀 AI PROJECT MASTER LAUNCHER (Shared Virtual Env)
# Automatically starts all apps and the dashboard
# ===============================================

BASE_DIR="$(pwd)"
SHARED_VENV="$BASE_DIR/shared_venv"

# Activate shared virtual environment
if [ -d "$SHARED_VENV" ]; then
    echo "🔹 Activating shared virtual environment..."
    source "$SHARED_VENV/bin/activate"
else
    echo "⚠️ Shared virtual environment not found! Please create shared_venv first."
    exit 1
fi

# Format: ["folder"]="port custom_command"
declare -A APPS
APPS["ai_interview_app"]="8001 uvicorn app:app --reload"
APPS["ai-safe-chat-guard"]="8502 streamlit run app/webapp.py"   # adjust path if needed
APPS["fashion_search_bot"]="8003 uvicorn backend.main:app --reload"
APPS["LegalMind"]="8004 uvicorn app:app --reload"
APPS["object_detect-info"]="8005 uvicorn app.orchestrator:app --reload"
APPS["Personalized_Shopping_Recommendation"]="8006 uvicorn backend.main:app --reload"
APPS["review-analzer"]="8007 python app.py"

echo "🔹 Starting all AI apps..."

for APP in "${!APPS[@]}"; do
    IFS=' ' read -r PORT CMD <<< "${APPS[$APP]}"
    echo "➡️  Starting $APP on port $PORT..."
    
    cd "$BASE_DIR/$APP" || continue

    # Run the command in the background
    if [[ $CMD == streamlit* ]]; then
        $CMD --server.port "$PORT" &
    else
        $CMD --port "$PORT" &
    fi
    
    sleep 2
done

# Start the dashboard last
cd "$BASE_DIR/ai_project_hub" || exit
echo "🚀 Launching Dashboard..."
uvicorn main:app --reload --port 9000 &

# Open dashboard in browser after short delay
sleep 5
xdg-open "http://127.0.0.1:9000"

echo "✅ All apps started! Dashboard opened at http://127.0.0.1:9000"
