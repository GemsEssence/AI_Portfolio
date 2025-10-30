const chatWindow = document.getElementById('chatWindow');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const imageFile = document.getElementById('imageFile');
const voiceFile = document.getElementById('voiceFile');

// ✅ Function to add message bubble
function addMessage(content, sender = 'user', type = 'text') {
  const msg = document.createElement('div');
  msg.classList.add('message', sender === 'user' ? 'user-msg' : 'bot-msg');

  if (type === 'image') {
    const imgContainer = document.createElement('div');
    imgContainer.classList.add('chat-image-container');
    const img = document.createElement('img');
    img.src = content;
    img.alt = 'Uploaded image';
    img.classList.add('chat-image');
    imgContainer.appendChild(img);
    msg.appendChild(imgContainer);
  } else {
    msg.innerHTML = content; // allow <b>, <br> etc.
  }

  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return msg;
}

// ✅ Typing/Analyzing loader animation
function showTypingLoader() {
  const msg = document.createElement('div');
  msg.classList.add('message', 'bot-msg');

  const loader = document.createElement('div');
  loader.classList.add('typing-loader');
  loader.innerHTML = '<span></span><span></span><span></span>';

  msg.appendChild(loader);
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return msg;
}

// Generate or reuse session ID for memory
// ✅ Persistent Session ID (per browser tab)
let sessionId = localStorage.getItem("medibot_session");
if (!sessionId) {
  sessionId = "session_" + Math.random().toString(36).substring(2, 10);
  localStorage.setItem("medibot_session", sessionId);
  console.log("🧠 Created new session:", sessionId);
} else {
  console.log("🔁 Reusing existing session:", sessionId);
}

// 🩺 Function: Show long bot reply in chunks
// function showBotResponseGradually(fullText) {
//   // Split the response only by double newlines for natural pacing
//   const parts = fullText
//     .split(/\n\s*\n/) // split by blank lines or paragraph breaks
//     .map(t => t.trim())
//     .filter(t => t.length > 0);

//   let delay = 0;
//   for (const part of parts) {
//     delay += 1200; // 1.2 second delay between parts (adjust as needed)
//     setTimeout(() => {
//       addMessage(part, 'bot');
//     }, delay);
//   }
// }
function showBotResponseGradually(fullText) {
  // Normalize line breaks and split into logical message parts
  const parts = fullText
    .split(/\n+/) // split on one or more line breaks
    .map(t => t.trim())
    .filter(t => t.length > 0);

  let delay = 0;

  for (const part of parts) {
    delay += 1200; // Delay between each message block

    setTimeout(() => {
      // Convert **bold** markdown syntax to <strong> tags
      const formatted = part.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      addMessage(formatted, 'bot', true); // pass HTML flag
    }, delay);
  }
}


// ✅ Handle text query with typing animation
// ✅ Send message when clicking the send button
sendBtn.addEventListener('click', sendMessage);

// ✅ Send message when pressing Enter
textInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault(); // prevent newline
    sendMessage();
  }
});

// ✅ Main send function
async function sendMessage() {
  const text = textInput.value.trim();
  if (!text) return;

  addMessage(text, 'user');
  textInput.value = '';

  const typingMsg = showTypingLoader();

  try {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('session_id', sessionId);

    const response = await fetch('/text', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    console.log("🩺 MediBot Response:", data);

    if (typingMsg && chatWindow.contains(typingMsg))
      chatWindow.removeChild(typingMsg);

    if (data?.response) {
      showBotResponseGradually(data.response);
    } else if (data?.message) {
      addMessage("⚠️ " + data.message, 'bot');
    } else {
      addMessage("🤖 I didn’t quite get that. Could you rephrase?", 'bot');
    }

  } catch (err) {
    console.error("Text message error:", err);
    if (typingMsg && chatWindow.contains(typingMsg))
      chatWindow.removeChild(typingMsg);
    addMessage("⚠️ There was an issue processing your message.", 'bot');
  }
}



// ✅ Handle image upload (doctor-friendly + scanning animation)
imageFile.addEventListener('change', async () => {
    const file = imageFile.files[0];
    if (!file) return;
  
    const imageURL = URL.createObjectURL(file);
    const userImageMsg = addMessage(imageURL, 'user', 'image');
  
    const imgContainer = userImageMsg.querySelector('.chat-image-container');
    if (imgContainer) imgContainer.classList.add('loading'); // shimmer border
  
    const typingMsg = showTypingLoader();
  
    const formData = new FormData();
    formData.append('file', file);
  
    try {
      const response = await fetch('/image', { method: 'POST', body: formData });
      const data = await response.json();
  
      console.log("response-data =================>", data);
  
      if (imgContainer) imgContainer.classList.remove('loading');
      if (typingMsg && chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);
  
      // 🩺 Safely extract doctor response
      let doctorText = data?.reply?.doctor_response || data?.analysis?.doctor_response?.doctor_response;
      if (!doctorText) {
        addMessage("⚠️ Couldn’t understand the medical image. Please try again.", 'bot');
        return;
      }
  
      // Clean up markdown code block syntax
      doctorText = doctorText.replace(/```json|```/g, '').trim();
  
      let doctorJSON;
      try {
        doctorJSON = JSON.parse(doctorText);
      } catch (err) {
        console.error("Failed to parse doctor response JSON:", err);
        addMessage("⚠️ Error reading analysis details.", 'bot');
        return;
      }
  
      // 🧠 Convert JSON into structured animated cards
      const sections = [
        { title: "Diagnosis", value: doctorJSON.diagnosis },
        { title: "Explanation", value: doctorJSON.explanation },
        { title: "Possible Causes", value: doctorJSON.possible_causes?.join(", ") },
        { title: "Recommended Medicines", value: doctorJSON.recommended_medicines?.join(", ") },
        { title: "Home Remedies", value: doctorJSON.home_remedies?.join(", ") },
        { title: "Precautions", value: doctorJSON.precautions?.join(", ") },
        { title: "Follow-up Question", value: doctorJSON.follow_up_question }
      ].filter(s => s.value);
  
      // Add delay between cards to simulate realistic AI typing
      let delay = 0;
      for (const section of sections) {
        delay += 1000; // 1-second gap
        setTimeout(() => {
          const msg = document.createElement('div');
          msg.className = "message bot-msg bot-card fade-in";
          msg.innerHTML = `
            <h4>${section.title}</h4>
            <p>${section.value}</p>
          `;
          chatWindow.appendChild(msg);
          chatWindow.scrollTop = chatWindow.scrollHeight;
        }, delay);
      }
  
    } catch (error) {
      console.error("Image analysis error:", error);
      if (imgContainer) imgContainer.classList.remove('loading');
      if (typingMsg && chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);
      addMessage("⚠️ Error analyzing image. Please retry.", 'bot');
    } finally {
      imageFile.value = '';
    }
  });
  
  
// ✅ Handle voice input upload
voiceFile.addEventListener('change', async () => {
  const file = voiceFile.files[0];
  if (!file) return;

  addMessage('🎤 Voice input uploaded...', 'user');
  const typingMsg = showTypingLoader();

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/voice', { method: 'POST', body: formData });
    const data = await response.json();

    chatWindow.removeChild(typingMsg);
    addMessage(data.transcription || "Sorry, I couldn’t process your voice.", 'bot');
  } catch (error) {
    chatWindow.removeChild(typingMsg);
    addMessage("⚠️ Error processing voice input.", 'bot');
  } finally {
    voiceFile.value = '';
  }
});
