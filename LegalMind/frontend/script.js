// ===== Chat: Ask question =====
async function askQuestion() {
    const questionInput = document.getElementById("question");
    const chatBox = document.getElementById("chat-box");
  
    const question = questionInput.value.trim();
    if (!question) return;
  
    // Show user message
    const userMsg = document.createElement("div");
    userMsg.className = "message user-message";
    userMsg.textContent = question;
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
  
    questionInput.value = "";
  
    // Show "loading" message while fetching
    const loadingMsg = document.createElement("div");
    loadingMsg.className = "message bot-message loading";
    loadingMsg.textContent = "⏳ Thinking...";
    chatBox.appendChild(loadingMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
  
    try {
      const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 3 }),
      });
      const data = await res.json();
  
      // Remove loading message
      chatBox.removeChild(loadingMsg);
  
      // Handle empty or insufficient context
      let answer = data.answer;
      if (!answer || answer.trim().toUpperCase() === "INSUFFICIENT CONTEXT" || answer.trim() === "") {
        answer = "❌ Sorry, I could not find a relevant answer to your query.";
      }
  
      // Show bot answer
      const botMsg = document.createElement("div");
      botMsg.className = "message bot-message";
  
      let html = `<b>Answer:</b> ${answer}`;
      if (data.retrieval && data.retrieval.length > 0) {
        html += `<br><br><b>Source:</b><br>` +
                data.retrieval.map(
                  r => `📄 ${r.source} (page no.${r.page}): ${r.text}`
                ).join("<br><br>");
      }
  
      botMsg.innerHTML = html;
      chatBox.appendChild(botMsg);
      chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
      console.error("Error:", err);
      chatBox.removeChild(loadingMsg);
  
      const errMsg = document.createElement("div");
      errMsg.className = "message bot-message error";
      errMsg.textContent = "⚠️ Error: Could not get response from server.";
      chatBox.appendChild(errMsg);
    }
  }
  
  
  // ===== PDF Upload =====
  document.getElementById("uploadForm").onsubmit = async function(e) {
    e.preventDefault();
    const file = document.getElementById("fileInput").files[0];
    if (!file) {
      alert("Please select a PDF file to upload.");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", file);
  
    const statusEl = document.getElementById("upload-status");
    statusEl.innerText = "⏳ Uploading...";
  
    try {
      const res = await fetch("/upload", { method: "POST", body: formData });
      const data = await res.json();
      statusEl.innerText = "✅ PDF uploaded and indexed successfully!";
      setTimeout(() => statusEl.innerText = "", 3000); // remove after 3s
    } catch (err) {
      console.error(err);
      statusEl.innerText = "❌ Upload failed.";
      setTimeout(() => statusEl.innerText = "", 3000); // remove after 3s
    }
  };
  