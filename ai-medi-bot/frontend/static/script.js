// const chatWindow = document.getElementById('chatWindow');
// const textInput = document.getElementById('textInput');
// const sendBtn = document.getElementById('sendBtn');
// const imageFile = document.getElementById('imageFile');
// const voiceFile = document.getElementById('voiceFile');

// // ✅ Function to add message bubble
// function addMessage(content, sender = 'user', type = 'text') {
//   const msg = document.createElement('div');
//   msg.classList.add('message', sender === 'user' ? 'user-msg' : 'bot-msg');

//   if (type === 'image') {
//     const imgContainer = document.createElement('div');
//     imgContainer.classList.add('chat-image-container');
//     const img = document.createElement('img');
//     img.src = content;
//     img.alt = 'Uploaded image';
//     img.classList.add('chat-image');
//     imgContainer.appendChild(img);
//     msg.appendChild(imgContainer);
//   } else {
//     msg.innerHTML = content; // allow <b>, <br> etc.
//   }

//   chatWindow.appendChild(msg);
//   chatWindow.scrollTop = chatWindow.scrollHeight;
//   return msg;
// }

// // ✅ Typing/Analyzing loader animation
// function showTypingLoader() {
//   const msg = document.createElement('div');
//   msg.classList.add('message', 'bot-msg');

//   const loader = document.createElement('div');
//   loader.classList.add('typing-loader');
//   loader.innerHTML = '<span></span><span></span><span></span>';

//   msg.appendChild(loader);
//   chatWindow.appendChild(msg);
//   chatWindow.scrollTop = chatWindow.scrollHeight;
//   return msg;
// }

// // Generate or reuse session ID for memory
// // ✅ Persistent Session ID (per browser tab)
// let sessionId = localStorage.getItem("medibot_session");
// if (!sessionId) {
//   sessionId = "session_" + Math.random().toString(36).substring(2, 10);
//   localStorage.setItem("medibot_session", sessionId);
//   console.log("🧠 Created new session:", sessionId);
// } else {
//   console.log("🔁 Reusing existing session:", sessionId);
// }

// // 🩺 Function: Show long bot reply in chunks
// // function showBotResponseGradually(fullText) { 
// //   // Split the response only by double newlines for natural pacing
// //   const parts = fullText
// //     .split(/\n\s*\n/) // split by blank lines or paragraph breaks
// //     .map(t => t.trim())
// //     .filter(t => t.length > 0);

// //   let delay = 0;
// //   for (const part of parts) {
// //     delay += 1200; // 1.2 second delay between parts (adjust as needed)
// //     setTimeout(() => {
// //       addMessage(part, 'bot');
// //     }, delay);
// //   }
// // }
// function showBotResponseGradually(fullText) {
//   // Normalize line breaks and split into logical message parts
//   const parts = fullText
//     .split(/\n+/) // split on one or more line breaks
//     .map(t => t.trim())
//     .filter(t => t.length > 0);

//   let delay = 0;

//   for (const part of parts) {
//     delay += 1200; // Delay between each message block

//     setTimeout(() => {
//       // Convert **bold** markdown syntax to <strong> tags
//       const formatted = part.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
//       addMessage(formatted, 'bot', true); // pass HTML flag
//     }, delay);
//   }
// }


// // ✅ Handle text query with typing animation
// // ✅ Send message when clicking the send button
// sendBtn.addEventListener('click', sendMessage);

// // ✅ Send message when pressing Enter
// textInput.addEventListener('keydown', (event) => {
//   if (event.key === 'Enter' && !event.shiftKey) {
//     event.preventDefault(); // prevent newline
//     sendMessage();
//   }
// });

// // ✅ Main send function
// async function sendMessage() {
//   const text = textInput.value.trim();
//   if (!text) return;

//   addMessage(text, 'user');
//   textInput.value = '';

//   const typingMsg = showTypingLoader();

//   try {
//     const formData = new FormData();
//     formData.append('text', text);
//     formData.append('session_id', sessionId);

//     const response = await fetch('/text', {
//       method: 'POST',
//       body: formData
//     });

//     const data = await response.json();
//     console.log("🩺 MediBot Response:", data);

//     if (typingMsg && chatWindow.contains(typingMsg))
//       chatWindow.removeChild(typingMsg);

//     if (data?.response) {
//       showBotResponseGradually(data.response);
//     } else if (data?.message) {
//       addMessage("⚠️ " + data.message, 'bot');
//     } else {
//       addMessage("🤖 I didn’t quite get that. Could you rephrase?", 'bot');
//     }

//   } catch (err) {
//     console.error("Text message error:", err);
//     if (typingMsg && chatWindow.contains(typingMsg))
//       chatWindow.removeChild(typingMsg);
//     addMessage("⚠️ There was an issue processing your message.", 'bot');
//   }
// }



// // ✅ Handle image upload (doctor-friendly + scanning animation)
// imageFile.addEventListener('change', async () => {
//     const file = imageFile.files[0];
//     if (!file) return;
  
//     const imageURL = URL.createObjectURL(file);
//     const userImageMsg = addMessage(imageURL, 'user', 'image');
  
//     const imgContainer = userImageMsg.querySelector('.chat-image-container');
//     if (imgContainer) imgContainer.classList.add('loading'); // shimmer border
  
//     const typingMsg = showTypingLoader();
  
//     const formData = new FormData();
//     formData.append('file', file);
  
//     try {
//       const response = await fetch('/image', { method: 'POST', body: formData });
//       const data = await response.json();
  
//       console.log("response-data =================>", data);
  
//       if (imgContainer) imgContainer.classList.remove('loading');
//       if (typingMsg && chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);
  
//       // 🩺 Safely extract doctor response
//       let doctorText = data?.reply?.doctor_response || data?.analysis?.doctor_response?.doctor_response;
//       if (!doctorText) {
//         addMessage("⚠️ Couldn’t understand the medical image. Please try again.", 'bot');
//         return;
//       }
  
//       // Clean up markdown code block syntax
//       doctorText = doctorText.replace(/```json|```/g, '').trim();
  
//       let doctorJSON;
//       try {
//         doctorJSON = JSON.parse(doctorText);
//       } catch (err) {
//         console.error("Failed to parse doctor response JSON:", err);
//         addMessage("⚠️ Error reading analysis details.", 'bot');
//         return;
//       }
  
//       // 🧠 Convert JSON into structured animated cards
//       const sections = [
//         { title: "Diagnosis", value: doctorJSON.diagnosis },
//         { title: "Explanation", value: doctorJSON.explanation },
//         { title: "Possible Causes", value: doctorJSON.possible_causes?.join(", ") },
//         { title: "Recommended Medicines", value: doctorJSON.recommended_medicines?.join(", ") },
//         { title: "Home Remedies", value: doctorJSON.home_remedies?.join(", ") },
//         { title: "Precautions", value: doctorJSON.precautions?.join(", ") },
//         { title: "Follow-up Question", value: doctorJSON.follow_up_question }
//       ].filter(s => s.value);
  
//       // Add delay between cards to simulate realistic AI typing
//       let delay = 0;
//       for (const section of sections) {
//         delay += 1000; // 1-second gap
//         setTimeout(() => {
//           const msg = document.createElement('div');
//           msg.className = "message bot-msg bot-card fade-in";
//           msg.innerHTML = `
//             <h4>${section.title}</h4>
//             <p>${section.value}</p>
//           `;
//           chatWindow.appendChild(msg);
//           chatWindow.scrollTop = chatWindow.scrollHeight;
//         }, delay);
//       }
  
//     } catch (error) {
//       console.error("Image analysis error:", error);
//       if (imgContainer) imgContainer.classList.remove('loading');
//       if (typingMsg && chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);
//       addMessage("⚠️ Error analyzing image. Please retry.", 'bot');
//     } finally {
//       imageFile.value = '';
//     }
//   });
  
  
// // ✅ Handle voice input upload
// voiceFile.addEventListener('change', async () => {
//   const file = voiceFile.files[0];
//   if (!file) return;

//   addMessage('🎤 Voice input uploaded...', 'user');
//   const typingMsg = showTypingLoader();

//   const formData = new FormData();
//   formData.append('file', file);

//   try {
//     const response = await fetch('/voice', { method: 'POST', body: formData });
//     const data = await response.json();

//     chatWindow.removeChild(typingMsg);
//     addMessage(data.transcription || "Sorry, I couldn’t process your voice.", 'bot');
//   } catch (error) {
//     chatWindow.removeChild(typingMsg);
//     addMessage("⚠️ Error processing voice input.", 'bot');
//   } finally {
//     voiceFile.value = '';
//   }
// });
// 🌍 Global Elements
const chatWindow = document.getElementById('chatWindow');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const imageFile = document.getElementById('imageFile');
const voiceFile = document.getElementById('voiceFile');
const languageSelect = document.getElementById('languageSelect');
const headerTitle = document.querySelector(".chat-header h1");
const headerSubtitle = document.querySelector(".chat-header p");

// 🧩 UI Text (titles, subtitles, placeholders)
const uiText = {
  en: { title: "🤖 AI MediBot", subtitle: "Your healthcare assistant", placeholder: "Type your symptoms or message..." },
  hi: { title: "🤖 एआई मेडिबॉट", subtitle: "आपका स्वास्थ्य सहायक", placeholder: "अपने लक्षण या संदेश टाइप करें..." },
  es: { title: "🤖 AI MediBot", subtitle: "Su asistente de atención médica", placeholder: "Escribe tus síntomas o mensaje..." },
  fr: { title: "🤖 AI MediBot", subtitle: "Votre assistant de santé", placeholder: "Tapez vos symptômes ou votre message..." },
  ja: { title: "🤖 AIメディボット", subtitle: "あなたのヘルスケアアシスタント", placeholder: "症状やメッセージを入力してください..." },
  zh: { title: "🤖 AI 医疗助手", subtitle: "您的健康助手", placeholder: "请输入您的症状或信息..." },
  ru: { title: "🤖 AI Медибот", subtitle: "Ваш помощник по здоровью", placeholder: "Введите свои симптомы или сообщение..." },
  ar: { title: "🤖 المساعد الطبي الذكي", subtitle: "مساعدك الصحي", placeholder: "اكتب أعراضك أو رسالتك..." }
};

// 🌍 Localized Error Messages
const errorMessages = {
  en: {
    busy: "⚠️ Server is busy. Please wait a minute and try again.",
    serverError: "⚠️ Server error occurred. Please try again later.",
    imageFail: "⚠️ Couldn’t understand the medical image. Please try again.",
    aiOverload: "⚠️ The AI system is temporarily overloaded. Please retry after 1–2 minutes.",
    textFail: "⚠️ There was an issue processing your message.",
    voiceFail: "⚠️ Error processing voice input.",
    analysisError: "⚠️ Error analyzing image. Please retry.",
    identifiableImage: "⚠️ For privacy reasons, please upload only the affected area (not a full-face or identifiable image)."
  },
  hi: {
    busy: "⚠️ सर्वर व्यस्त है। कृपया एक मिनट प्रतीक्षा करें और पुनः प्रयास करें।",
    serverError: "⚠️ सर्वर में त्रुटि हुई। कृपया बाद में पुनः प्रयास करें।",
    imageFail: "⚠️ छवि को समझा नहीं जा सका। कृपया पुनः प्रयास करें।",
    aiOverload: "⚠️ एआई प्रणाली अस्थायी रूप से ओवरलोड है। कृपया 1–2 मिनट बाद पुनः प्रयास करें।",
    textFail: "⚠️ आपके संदेश को संसाधित करने में समस्या हुई।",
    voiceFail: "⚠️ वॉयस इनपुट संसाधित करने में त्रुटि हुई।",
    analysisError: "⚠️ छवि का विश्लेषण करते समय त्रुटि हुई। कृपया पुनः प्रयास करें।",
    identifiableImage: "⚠️ गोपनीयता कारणों से कृपया केवल प्रभावित क्षेत्र की छवि अपलोड करें (पूरा चेहरा या पहचान योग्य छवि नहीं)।"
  },
  es: {
    busy: "⚠️ El servidor está ocupado. Espere un minuto y vuelva a intentarlo.",
    serverError: "⚠️ Ocurrió un error en el servidor. Inténtelo de nuevo más tarde.",
    imageFail: "⚠️ No se pudo entender la imagen médica. Inténtelo nuevamente.",
    aiOverload: "⚠️ El sistema de IA está sobrecargado temporalmente. Intente de nuevo en 1–2 minutos.",
    textFail: "⚠️ Hubo un problema al procesar su mensaje.",
    voiceFail: "⚠️ Error al procesar la entrada de voz.",
    analysisError: "⚠️ Error al analizar la imagen. Inténtelo nuevamente.",
    identifiableImage: "⚠️ Por razones de privacidad, cargue solo el área afectada (no una imagen de rostro completo o identificable)."
  },
  fr: {
    busy: "⚠️ Le serveur est occupé. Veuillez patienter une minute et réessayer.",
    serverError: "⚠️ Une erreur serveur s’est produite. Réessayez plus tard.",
    imageFail: "⚠️ Impossible de comprendre l'image médicale. Réessayez.",
    aiOverload: "⚠️ Le système d'IA est temporairement surchargé. Réessayez dans 1–2 minutes.",
    textFail: "⚠️ Problème lors du traitement de votre message.",
    voiceFail: "⚠️ Erreur lors du traitement de la voix.",
    analysisError: "⚠️ Erreur d’analyse de l’image. Réessayez.",
    identifiableImage: "⚠️ Pour des raisons de confidentialité, veuillez télécharger uniquement la zone affectée (pas une image complète du visage ou identifiable)."
  },
  ja: {
    busy: "⚠️ サーバーが混雑しています。1分ほど待ってから再試行してください。",
    serverError: "⚠️ サーバーエラーが発生しました。後でもう一度お試しください。",
    imageFail: "⚠️ 医用画像を理解できませんでした。再試行してください。",
    aiOverload: "⚠️ AIシステムが一時的に過負荷です。1〜2分後に再試行してください。",
    textFail: "⚠️ メッセージの処理中に問題が発生しました。",
    voiceFail: "⚠️ 音声入力の処理中にエラーが発生しました。",
    analysisError: "⚠️ 画像解析中にエラーが発生しました。再試行してください。",
    identifiableImage: "⚠️ プライバシー保護のため、顔全体や個人を特定できる画像ではなく、患部のみをアップロードしてください。"
  },
  zh: {
    busy: "⚠️ 服务器繁忙，请稍等一分钟后重试。",
    serverError: "⚠️ 服务器错误，请稍后再试。",
    imageFail: "⚠️ 无法理解医疗图像，请重试。",
    aiOverload: "⚠️ AI系统暂时过载，请1-2分钟后再试。",
    textFail: "⚠️ 处理您的消息时出现问题。",
    voiceFail: "⚠️ 处理语音输入时出错。",
    analysisError: "⚠️ 分析图像时出错，请重试。",
    identifiableImage: "⚠️ 出于隐私原因，请仅上传受影响的区域（不要上传完整面部或可识别的图像）。"
  },
  ru: {
    busy: "⚠️ Сервер занят. Подождите минуту и попробуйте снова.",
    serverError: "⚠️ Произошла ошибка сервера. Попробуйте позже.",
    imageFail: "⚠️ Не удалось распознать медицинское изображение. Попробуйте снова.",
    aiOverload: "⚠️ Система ИИ временно перегружена. Повторите через 1–2 минуты.",
    textFail: "⚠️ Ошибка при обработке вашего сообщения.",
    voiceFail: "⚠️ Ошибка при обработке голосового ввода.",
    analysisError: "⚠️ Ошибка при анализе изображения. Повторите попытку.",
    identifiableImage: "⚠️ По соображениям конфиденциальности загрузите только пораженную область (не полное лицо или распознаваемое изображение)."
  },
  ar: {
    busy: "⚠️ الخادم مشغول. يرجى الانتظار دقيقة ثم المحاولة مرة أخرى.",
    serverError: "⚠️ حدث خطأ في الخادم. حاول مرة أخرى لاحقًا.",
    imageFail: "⚠️ لم يتم فهم الصورة الطبية. يرجى المحاولة مرة أخرى.",
    aiOverload: "⚠️ النظام الذكي محمّل مؤقتًا. أعد المحاولة بعد 1-2 دقيقة.",
    textFail: "⚠️ حدثت مشكلة أثناء معالجة رسالتك.",
    voiceFail: "⚠️ خطأ أثناء معالجة الإدخال الصوتي.",
    analysisError: "⚠️ خطأ أثناء تحليل الصورة. يرجى المحاولة مرة أخرى.",
    identifiableImage: "⚠️ لأسباب تتعلق بالخصوصية، يرجى تحميل المنطقة المصابة فقط (وليس صورة الوجه الكاملة أو الصورة القابلة للتعرف عليها)."
  }
};

// 🈯 Update UI on language change
languageSelect.addEventListener("change", () => {
  const lang = languageSelect.value;
  const text = uiText[lang] || uiText["en"];
  headerTitle.innerText = text.title;
  headerSubtitle.innerText = text.subtitle;
  textInput.placeholder = text.placeholder;
});

// 🗨️ Add message bubble
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
  } else msg.innerHTML = content;
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return msg;
}

// 💬 Typing loader
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

// 🧠 Persistent Session
let sessionId = localStorage.getItem("medibot_session");
if (!sessionId) {
  sessionId = "session_" + Math.random().toString(36).substring(2, 10);
  localStorage.setItem("medibot_session", sessionId);
  console.log("🧠 Created new session:", sessionId);
} else console.log("🔁 Reusing existing session:", sessionId);

// 🧩 Gradual reply display
function showBotResponseGradually(fullText) {
  const parts = fullText.split(/\n+/).map(t => t.trim()).filter(t => t.length > 0);
  let delay = 0;
  for (const part of parts) {
    delay += 1200;
    setTimeout(() => {
      const formatted = part.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      addMessage(formatted, 'bot');
    }, delay);
  }
}

// 📝 Send text
sendBtn.addEventListener('click', sendMessage);
textInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

async function sendMessage() {
  const text = textInput.value.trim();
  const lang = languageSelect.value;
  const err = errorMessages[lang] || errorMessages.en;

  if (!text) return;
  addMessage(text, 'user');
  textInput.value = '';
  const typingMsg = showTypingLoader();

  try {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('session_id', sessionId);
    formData.append('lang', lang);

    const response = await fetch('/text', { method: 'POST', body: formData });
    const data = await response.json();
    chatWindow.removeChild(typingMsg);

    if (data?.response) showBotResponseGradually(data.response);
    else if (data?.message) addMessage("⚠️ " + data.message, 'bot');
    else addMessage("🤖 I didn’t quite get that. Could you rephrase?", 'bot');
  } catch (error) {
    console.error("Text message error:", error);
    if (chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);
    addMessage(err.textFail, 'bot');
  }
}

// 📸 Handle image upload
imageFile.addEventListener('change', async () => {
  const file = imageFile.files[0];
  if (!file) return;
  const lang = languageSelect.value;
  const err = errorMessages[lang] || errorMessages.en;

  const imageURL = URL.createObjectURL(file);
  const userImageMsg = addMessage(imageURL, 'user', 'image');
  const imgContainer = userImageMsg.querySelector('.chat-image-container');
  if (imgContainer) imgContainer.classList.add('loading');
  const typingMsg = showTypingLoader();

  const formData = new FormData();
  formData.append('file', file);

    try {
      const response = await fetch(`/image?lang=${lang}`, { method: 'POST', body: formData });
      if (!response.ok) {
        if (response.status === 429) return addMessage(err.busy, 'bot');
        if (response.status >= 500) return addMessage(err.serverError, 'bot');
      }

      const data = await response.json();
      console.log("📸 Image response:", data);
      if (imgContainer) imgContainer.classList.remove('loading');
      if (chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);

      const doctorData = data?.reply || data?.analysis?.doctor_response;
      if (!doctorData) return addMessage(err.imageFail, 'bot');

      const errorMessage = doctorData?.error || doctorData?.doctor_response;
      if (errorMessage?.includes("429") || errorMessage?.toLowerCase().includes("resource exhausted")) {
        return addMessage(err.aiOverload, 'bot');
      }

      const label = data?.analysis?.label || "";
      if (label.toLowerCase().includes("rejected")) {
        const rejectionMessage = errorMessages[lang]?.identifiableImage || errorMessages["en"].identifiableImage;
        return addMessage(rejectionMessage, 'bot');
      }

    const titles = {
      en: { diagnosis: "Disease", explanation: "Explanation", causes: "Possible Causes", medicines: "Recommended Medicines", remedies: "Home Remedies", precautions: "Precautions", followup: "Follow-up Question" },
      hi: { diagnosis: "बीमारी", explanation: "व्याख्या", causes: "संभावित कारण", medicines: "सिफारिश की गई दवाएं", remedies: "घरेलू उपचार", precautions: "सावधानियां", followup: "फॉलो-अप प्रश्न" },
      es: { diagnosis: "Enfermedad", explanation: "Explicación", causes: "Posibles causas", medicines: "Medicamentos recomendados", remedies: "Remedios caseros", precautions: "Precauciones", followup: "Pregunta de seguimiento" },
      fr: { diagnosis: "Maladie", explanation: "Explication", causes: "Causes possibles", medicines: "Médicaments recommandés", remedies: "Remèdes maison", precautions: "Précautions", followup: "Question de suivi" },
      ja: { diagnosis: "病名", explanation: "説明", causes: "考えられる原因", medicines: "推奨される薬", remedies: "家庭療法", precautions: "注意事項", followup: "フォローアップの質問" },
      zh: { diagnosis: "疾病", explanation: "解释", causes: "可能原因", medicines: "推荐药物", remedies: "家庭疗法", precautions: "注意事项", followup: "后续问题" },
      ru: { diagnosis: "Заболевание", explanation: "Объяснение", causes: "Возможные причины", medicines: "Рекомендуемые лекарства", remedies: "Домашние средства", precautions: "Меры предосторожности", followup: "Последующий вопрос" },
      ar: { diagnosis: "المرض", explanation: "الشرح", causes: "الأسباب المحتملة", medicines: "الأدوية الموصى بها", remedies: "العلاجات المنزلية", precautions: "الاحتياطات", followup: "سؤال المتابعة" }
    }[lang] || titles.en;

    const sections = [
      { title: titles.diagnosis, value: doctorData.diagnosis },
      { title: titles.explanation, value: doctorData.explanation },
      { title: titles.causes, value: doctorData.possible_causes?.join(", ") },
      { title: titles.medicines, value: doctorData.recommended_medicines?.join(", ") },
      { title: titles.remedies, value: doctorData.home_remedies?.join(", ") },
      { title: titles.precautions, value: doctorData.precautions?.join(", ") },
      { title: titles.followup, value: doctorData.follow_up_question }
    ].filter(s => s.value);

    let delay = 0;
    for (const section of sections) {
      delay += 1000;
      setTimeout(() => {
        const msg = document.createElement('div');
        msg.className = "message bot-msg bot-card fade-in";
        msg.innerHTML = `<h4>${section.title}</h4><p>${section.value}</p>`;
        chatWindow.appendChild(msg);
        chatWindow.scrollTop = chatWindow.scrollHeight;
      }, delay);
    }

  } catch (error) {
    console.error("Image analysis error:", error);
    if (imgContainer) imgContainer.classList.remove('loading');
    if (chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);
    addMessage(err.analysisError, 'bot');
  } finally {
    imageFile.value = '';
  }
});

// 🎤 Voice input
voiceFile.addEventListener('change', async () => {
  const file = voiceFile.files[0];
  if (!file) return;
  const lang = languageSelect.value;
  const err = errorMessages[lang] || errorMessages.en;

  addMessage('🎤 Voice input uploaded...', 'user');
  const typingMsg = showTypingLoader();

  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`/voice?lang=${lang}`, { method: 'POST', body: formData });
    const data = await response.json();
    chatWindow.removeChild(typingMsg);
    addMessage(data.transcription || err.voiceFail, 'bot');
  } catch (error) {
    if (chatWindow.contains(typingMsg)) chatWindow.removeChild(typingMsg);
    addMessage(err.voiceFail, 'bot');
  } finally {
    voiceFile.value = '';
  }
});
