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
    // Remove code-like symbols and unwanted brackets
    let cleanText = text
        .replace(/[`{}<>]/g, "")      // remove backticks and braces
        .replace(/\(.*?\)/g, "")      // remove content inside parentheses
        .replace(/\s{2,}/g, " ")      // collapse multiple spaces
        .replace(/\n/g, ". ")         // replace newlines with pause
        .trim();

    const utter = new SpeechSynthesisUtterance(cleanText);
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
function lockInterviewUI(finalFeedback) {
    interviewFinished = true;
    answerInput.disabled = true;
    sendBtn.disabled = true;
    chatPanel.style.display = "none";
    document.querySelector(".setup-panel").style.display = "none";
    summaryPanel.style.display = "block";

    const summaryCards = document.getElementById("summaryCards");
    summaryCards.innerHTML = ""; // clear previous summary cards

    // Split into question blocks using "---" separator
    const questions = finalFeedback.split(/---+/);

    let totalScore = 0;
    let scoreCount = 0;
    let questionNumber = 0;

    questions.forEach((q) => {
        if (q.trim() === "") return;

        // Extract Question, Answer, Score, and Feedback
        const questionMatch = q.match(/\*\*Question\s*\d+:\*\*\s*(.*)/i);
        const answerMatch = q.match(/\*\*Candidate's Answer:\*\*\s*(.*)/i);
        const scoreMatch = q.match(/\*\*Score:\*\*\s*(\d+)/i);
        const feedbackMatch = q.match(/\*\*Feedback:\*\*\s*([\s\S]*)/i);

        const questionText = questionMatch ? questionMatch[1].trim() : "";
        const answerText = answerMatch ? answerMatch[1].trim() : "";
        const scoreValue = scoreMatch ? parseInt(scoreMatch[1]) : 0;
        const feedbackText = feedbackMatch ? feedbackMatch[1].trim() : "";

        // Skip question if no valid text found (missing or blank)
        if (!questionText) return;

        questionNumber++;
        totalScore += scoreValue;
        scoreCount++;

        // Create summary card for each valid question
        const card = document.createElement("div");
        card.className = "summary-card";
        card.innerHTML = `
            <h4>Question ${questionNumber}: ${questionText}</h4>
            <p><b>Candidate's Answer:</b> ${answerText || "(No answer provided)"}</p>
            <p><b>Score:</b> ${scoreValue}/10</p>
            <p><b>Feedback:</b> ${feedbackText || "(No feedback)"}</p>
        `;
        summaryCards.appendChild(card);
    });

    // Handle overall score and feedback
    const overallScore = scoreCount ? (totalScore / scoreCount).toFixed(2) : "0.00";
    overallScoreEl.textContent = `Overall Score: ${overallScore}/10`;
    overallFeedbackEl.textContent = "Detailed feedback provided above.";

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
