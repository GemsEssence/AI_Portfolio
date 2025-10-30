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
APPS["ai-safe-chat-guard"]="8502 streamlit run app/webapp.py --server.headless true"
APPS["fashion_search_bot"]="8003 uvicorn backend.main:app --reload"
APPS["LegalMind"]="8004 uvicorn app:app --reload"
APPS["object_detect-info"]="8005 uvicorn app.orchestrator:app --reload"
APPS["Personalized_Shopping_Recommendation"]="8006 uvicorn backend.main:app --reload"
APPS["ai-medi-bot"]="8007 uvicorn app.main:app --reload"
APPS["review-analzer"]="5000 python app.py"

echo "🔹 Starting all AI apps..."

for APP in "${!APPS[@]}"; do
    IFS=' ' read -r PORT CMD <<< "${APPS[$APP]}"
    echo "➡️  Preparing $APP on port $PORT..."
    
    cd "$BASE_DIR/$APP" || continue

    # Kill existing process using the port
    PID=$(lsof -t -i :"$PORT")
    if [ -n "$PID" ]; then
        echo "⚠️ Port $PORT is in use by PID $PID. Killing..."
        kill -9 $PID
        sleep 1
    fi

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
DASH_PORT=9000
# Kill dashboard port if occupied
PID=$(lsof -t -i :"$DASH_PORT")
if [ -n "$PID" ]; then
    echo "⚠️ Dashboard port $DASH_PORT is in use by PID $PID. Killing..."
    kill -9 $PID
    sleep 1
fi

echo "🚀 Launching Dashboard..."
uvicorn main:app --reload --port "$DASH_PORT" &

# Open dashboard in browser after short delay
sleep 5
xdg-open "http://127.0.0.1:$DASH_PORT"

echo "✅ All apps started! Dashboard opened at http://127.0.0.1:$DASH_PORT"
