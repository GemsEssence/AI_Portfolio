async function analyzeReview() {
    const reviewText = document.getElementById("reviewInput").value;
    const resultDiv = document.getElementById("result");

    if (!reviewText.trim()) {
        resultDiv.innerHTML = `<div class="ai-card"><p style='color: red;'>Please enter a review!</p></div>`;
        return;
    }

    resultDiv.innerHTML = `<div class="ai-card"><p>Analyzing with AI...</p></div>`;

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ review: reviewText })
        });

        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<div class="ai-card"><p style='color: red;'>Error: ${data.error}</p></div>`;
        } else {
            resultDiv.innerHTML = `
                <div class="ai-card">
                    <h3>AI Analysis Result:</h3>
                    <p><span class="label">Summary:</span> ${data.summary}</p>
                    <p><span class="label">Sentiment:</span> ${data.sentiment}</p>
                </div>
            `;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="ai-card"><p style='color: red;'>Error: ${err.message}</p></div>`;
    }
}
