async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const chatBox = document.getElementById("chat-box");

    if (!fileInput.files[0]) {
        alert("Please select an image first!");
        return;
    }

    const file = fileInput.files[0];

    // 1️⃣ Show user uploaded image only
    const userMsg = document.createElement("div");
    userMsg.className = "message user";

    const imgPreview = document.createElement("img");
    imgPreview.src = URL.createObjectURL(file);
    imgPreview.style.maxWidth = "150px";
    imgPreview.style.borderRadius = "10px";
    imgPreview.style.display = "block";

    userMsg.appendChild(imgPreview);
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;

    // 2️⃣ Send image to backend
    const formData = new FormData();
    formData.append("file", file);
    console.log("Uploading file:", file.name, file.size, file.type);

    try {
        const response = await fetch("/upload-dress/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        console.log("Response from backend:", data);

        // 3️⃣ Show only products
        if (data.products && data.products.length > 0) {
            data.products.forEach(p => {
                const prodMsg = document.createElement("div");
                prodMsg.className = "message bot product-card";
                prodMsg.style.display = "flex";
                prodMsg.style.alignItems = "center";
                prodMsg.style.marginBottom = "10px";

                // Correct innerHTML
                prodMsg.innerHTML = `
                    <img src="${p.thumbnail || '/static/img/placeholder.png'}" alt="${p.title}" width="60" style="border-radius:5px;">
                    <div style="margin-left:10px;">
                        <b>${p.title}</b><br>
                        <span style="color:#ff4081;">${p.price || "N/A"}</span><br>
                        <a href="${p.link}" target="_blank">View Product</a>
                    </div>
                `;

                chatBox.appendChild(prodMsg);
            });
        } else {
            const noResultMsg = document.createElement("div");
            noResultMsg.className = "message bot";
            noResultMsg.textContent = "❌ No products found.";
            chatBox.appendChild(noResultMsg);
        }

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        const errorMsg = document.createElement("div");
        errorMsg.className = "message bot";
        errorMsg.textContent = "⚠️ Error fetching data: " + error.message;
        chatBox.appendChild(errorMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
        console.error(error);
    }
}
