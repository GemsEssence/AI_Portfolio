async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const chatBox = document.getElementById("chat-box");
    const loadingDiv = document.getElementById("loading");

    if (!fileInput.files[0]) {
        alert("Please select an image first!");
        return;
    }

    const file = fileInput.files[0];

    // 1️⃣ Show user uploaded image
    const userMsg = document.createElement("div");
    userMsg.className = "message user";

    const imgPreview = document.createElement("img");
    imgPreview.src = URL.createObjectURL(file);
    imgPreview.style.maxWidth = "170px";
    imgPreview.style.borderRadius = "10px";
    imgPreview.style.display = "block";

    userMsg.appendChild(imgPreview);
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;

    // 2️⃣ Show loading
    loadingDiv.style.display = "flex";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload-dress/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        console.log("Response from backend:", data);

        // 3️⃣ Hide loading
        loadingDiv.style.display = "none";


        // 4️⃣ Show products
        if (data.products && data.products.length > 0) {
            const rowDiv = document.createElement("div");
            rowDiv.className = "product-card-row";
            data.products.forEach(p => {
                const prodMsg = document.createElement("div");
                prodMsg.className = "message bot product-card";

                prodMsg.innerHTML = `
                    <img src="${p.thumbnail || '/static/img/placeholder.png'}" alt="${p.title}">
                    <div style="margin-left:10px;">
                        <b>${p.title}</b><br>
                        <span style="color:#ff4081;">${p.price || "N/A"}</span><br>
                        <a href="${p.link}" target="_blank">View Product</a>
                    </div>
                `;

                rowDiv.appendChild(prodMsg);
            });
            chatBox.appendChild(rowDiv);
        } else {
            const noResultMsg = document.createElement("div");
            noResultMsg.className = "message bot";
            noResultMsg.textContent = "❌ No products found.";
            chatBox.appendChild(noResultMsg);
        }

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        loadingDiv.style.display = "none";
        const errorMsg = document.createElement("div");
        errorMsg.className = "message bot";
        errorMsg.textContent = "⚠️ Error fetching data: " + error.message;
        chatBox.appendChild(errorMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
        console.error(error);
    }
}
function refreshChat() {
    const chatBox = document.getElementById("chat-box");
    const fileInput = document.getElementById("imageInput");
    const loadingDiv = document.getElementById("loading");

    // Clear chat messages
    chatBox.innerHTML = "";

    // Clear file input
    fileInput.value = "";

    // Hide loading
    loadingDiv.style.display = "none";

    // Optionally, scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}
