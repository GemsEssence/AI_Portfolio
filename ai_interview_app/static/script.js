const chatBox = document.getElementById("chatBox");
const chatPanel = document.getElementById("chatPanel");
const summaryPanel = document.getElementById("summaryPanel");
const summaryCards = document.getElementById("summaryCards");
const overallScoreEl = document.getElementById("overallScore");
const overallFeedbackEl = document.getElementById("overallFeedback");
const answerInput = document.getElementById("answerInput");
const sendBtn = document.getElementById("sendBtn");
const restartBtn = document.getElementById("restartBtn");

let interviewTimer;
let interviewFinished = false;

// --------------------
// Utility: Speak text
// --------------------
function speakText(text) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    speechSynthesis.speak(utter);
}

// --------------------
// Add chat bubble
// --------------------
function addBubble(role, text){
    const p = document.createElement("p");
    p.innerHTML = `<b>${role === "candidate" ? "You" : "Interviewer"}:</b> ${text}`;
    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// --------------------
// Lock UI and show final evaluation
// --------------------
function lockInterviewUI(finalFeedback){
    interviewFinished = true;       // stop further answers
    answerInput.disabled = true;
    sendBtn.disabled = true;
    chatPanel.style.display = "none";   // hide chat panel
    document.querySelector(".setup-panel").style.display = "none"; // hide setup panel

    summaryPanel.style.display = "block";

    const summaryCards = document.getElementById("summaryCards");
    summaryCards.innerHTML = ""; // clear old cards

    // Split by questions using "---" as separator
    const questions = finalFeedback.split(/---+/);

    let totalScore = 0;
    let scoreCount = 0;

    questions.forEach((q, idx) => {
        if(q.trim() === "") return;

        // Extract Question, Answer, Score, Feedback using regex
        const questionMatch = q.match(/Question\s*\d+:\s*(.*)/i);
        const answerMatch = q.match(/Candidate's Answer:\s*(.*)/i);
        const scoreMatch = q.match(/Score:\s*(\d+)/i);
        const feedbackMatch = q.match(/Feedback:\s*([\s\S]*)/i);

        const questionText = questionMatch ? questionMatch[1].trim() : "(Question missing)";
        const answerText = answerMatch ? answerMatch[1].trim() : "(No answer provided)";
        const scoreValue = scoreMatch ? parseInt(scoreMatch[1]) : 0;
        const feedbackText = feedbackMatch ? feedbackMatch[1].trim() : "(No feedback)";

        totalScore += scoreValue;
        scoreCount++;

        const card = document.createElement("div");
        card.className = "summary-card";
        card.innerHTML = `
            <h4>Question ${idx + 1}: ${questionText}</h4>
            <p><b>Candidate's Answer:</b> ${answerText}</p>
            <p><b>Score:</b> ${scoreValue}/10</p>
            <p><b>Feedback:</b> ${feedbackText}</p>
        `;
        summaryCards.appendChild(card);
    });

    const overallScore = (scoreCount ? (totalScore / scoreCount) : 0).toFixed(2);
    document.getElementById("overallScore").textContent = `Overall Score: ${overallScore}/10`;
    document.getElementById("overallFeedback").textContent = "Detailed feedback provided above.";

    speakText("Interview finished. Here is your final evaluation.");
}


// --------------------
// Restart Interview
// --------------------
restartBtn.onclick = () => location.reload();

// --------------------
// Start Interview
// --------------------
document.getElementById("startBtn").onclick = async () => {
    const tech = document.getElementById("tech").value;
    const exp = document.getElementById("exp").value;
    const duration = document.getElementById("duration").value;

    if(!tech || !exp || !duration){
        alert("Please fill all fields!");
        return;
    }

    const formData = new FormData();
    formData.append("tech", tech);
    formData.append("exp", exp);
    formData.append("duration", duration);

    const res = await fetch("/start", { method: "POST", body: formData });
    const data = await res.json();

    chatPanel.style.display = "block";
    addBubble("interviewer", data.question);
    speakText(data.question);

    // Timer for automatic evaluation
    interviewTimer = setTimeout(async () => {
        if(!interviewFinished){
            const evalRes = await fetch("/finish", { method: "POST" });
            const evalData = await evalRes.json();
            lockInterviewUI(evalData.feedback);
        }
    }, duration * 60000);
};

// --------------------
// Send Answer
// --------------------
sendBtn.onclick = async () => {
    if(interviewFinished) return;

    const answer = answerInput.value.trim();
    if(!answer) return;

    addBubble("candidate", answer);
    answerInput.value = "";

    const formData = new FormData();
    formData.append("answer", answer);

    const res = await fetch("/answer", { method: "POST", body: formData });
    const data = await res.json();

    if(data.finished){
        clearTimeout(interviewTimer);
        lockInterviewUI(data.feedback);
    } else {
        addBubble("interviewer", data.question);
        speakText(data.question);
    }
};
