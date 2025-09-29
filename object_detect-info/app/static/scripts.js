function openUpload() {
    document.getElementById('content').innerHTML = `
        <form id="uploadForm">
            <input type="file" name="file" id="fileInput" />
            <button type="submit">Upload</button>
        </form>
        <div id="result"></div>
    `;
    document.getElementById('uploadForm').onsubmit = async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('fileInput');
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        const res = await fetch("/upload-image", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        document.getElementById('result').innerText = JSON.stringify(data, null, 2);
    }
}

function openCamera() {
    document.getElementById('content').innerHTML = `
        <video id="video" width="400" autoplay></video>
        <button onclick="stopCamera()">Stop Camera</button>
        <pre id="result"></pre>
    `;
    const video = document.getElementById('video');
    const resultEl = document.getElementById('result');
    navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        const interval = setInterval(async () => {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
            const formData = new FormData();
            formData.append("frame", blob, "frame.jpg");
            const res = await fetch("/camera-feed", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            resultEl.innerText = JSON.stringify(data, null, 2);
        }, 1000);
        video._interval = interval;
    });
}

function stopCamera() {
    const video = document.getElementById('video');
    if(video && video.srcObject){
        video.srcObject.getTracks().forEach(track => track.stop());
        clearInterval(video._interval);
    }
    document.getElementById('result').innerText = "Camera stopped.";
}