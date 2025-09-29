const chatBox = document.getElementById("chatBox");
const chatPanel = document.getElementById("chatPanel");
const answerInput = document.getElementById("answerInput");
let interviewTimer;

// Speak text
function speakText(text){
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    speechSynthesis.speak(utter);
}

// Add chat bubble
function addBubble(role, text){
    const p = document.createElement("p");
    p.innerHTML = `<b>${role === "candidate" ? "You" : "Interviewer"}:</b> ${text}`;
    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Start interview
document.getElementById("startBtn").onclick = async () => {
    const tech = document.getElementById("tech").value;
    const exp = document.getElementById("exp").value;
    const duration = document.getElementById("duration").value;

    const formData = new FormData();
    formData.append("tech", tech);
    formData.append("exp", exp);
    formData.append("duration", duration);

    const res = await fetch("/start", { method: "POST", body: formData });
    const data = await res.json();

    chatPanel.style.display = "block";
    addBubble("interviewer", data.question);
    speakText(data.question);

    interviewTimer = setTimeout(() => {
        alert("⏰ Interview time is over! Click 'Finish Interview'");
    }, duration*60000);
};

// Send answer
document.getElementById("sendBtn").onclick = async () => {
    const answer = answerInput.value;
    if(!answer) return;

    addBubble("candidate", answer); // show in chat

    const formData = new FormData();
    formData.append("answer", answer);

    const res = await fetch("/answer", { method: "POST", body: formData });
    const data = await res.json();

    if(!data.finished){
        addBubble("interviewer", data.question);
        speakText(data.question);
        // Keep candidate input visible
        answerInput.value = answer;
    } else {
        addBubble("interviewer", `📋 Final Feedback & Scores: ${data.feedback}`);
        clearTimeout(interviewTimer);
    }
};

// Finish interview manually
document.getElementById("finishBtn").onclick = async () => {
    const res = await fetch("/finish", { method: "POST" });
    const data = await res.json();
    addBubble("interviewer", `📋 Final Feedback & Scores:\n${JSON.stringify(data.feedback, null, 2)}`);
};
