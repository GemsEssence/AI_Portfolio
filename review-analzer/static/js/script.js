async function analyzeReview() {
    let reviewText = document.getElementById("reviewInput").value;
    let resultDiv = document.getElementById("result");

    if (!reviewText.trim()) {
        resultDiv.innerHTML = "<p style='color: red;'>Please enter a review!</p>";
        return;
    }

    resultDiv.innerHTML = "<p>Analyzing...</p>";

    let response = await fetch("/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ review: reviewText })
    });

    let data = await response.json();

    if (data.error) {
        resultDiv.innerHTML = `<p style='color: red;'>Error: ${data.error}</p>`;
    } else {
        resultDiv.innerHTML = `
            <h3>Analysis Result:</h3>
            <p><strong>Summary:</strong> ${data.summary}</p>
            <p><strong>Sentiment:</strong> ${data.sentiment}</p>
        `;
    }
}
