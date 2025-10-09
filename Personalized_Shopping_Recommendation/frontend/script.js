function showExistingCustomer() {
    document.getElementById('recommendations').innerHTML = '';

    document.getElementById('existing-form').style.display = 'block';
    document.getElementById('new-form').style.display = 'none';
}

function showNewCustomer() {
    document.getElementById('recommendations').innerHTML = '';

    document.getElementById('new-form').style.display = 'block';
    document.getElementById('existing-form').style.display = 'none';
}

function fetchRecommendations() {
    const customerId = document.getElementById('customer-id').value.trim();
    if (!customerId) {
        alert("Please enter a Customer ID.");
        return;
    }
    fetch(`/recommendations/${customerId}`)
        .then(response => {
            if (!response.ok) throw new Error("Customer not found or no recommendations.");
            return response.json();
        })
        .then(data => displayRecommendations(data))
        .catch(err => {
            console.error('Error:', err);
            document.getElementById('recommendations').innerHTML = "<p>Error: " + err.message + "</p>";
        });
}

function fetchNewRecommendations() {
    const age = parseInt(document.getElementById('age').value);
    const gender = document.getElementById('gender').value;
    const segment = document.getElementById('segment').value;

    if (isNaN(age) || age <= 0 || age > 120) {
        alert("Please enter a valid age.");
        return;
    }

    const newCustomer = { age, gender, segment };

    fetch('/recommendations/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCustomer)
    })
    .then(response => {
        if (!response.ok) throw new Error("Invalid input.");
        return response.json();
    })
    .then(data => displayRecommendations(data))
    .catch(err => {
        console.error('Error:', err);
        document.getElementById('recommendations').innerHTML = "<p>Error: " + err.message + "</p>";
    });
}

function displayRecommendations(recs) {
    const container = document.getElementById('recommendations');
    container.innerHTML = "<h3>💡 AI-Powered Recommendations:</h3>";
    
    recs.forEach((rec, index) => {
        container.innerHTML += `
            <div class="recommendation ai-card" style="animation-delay: ${index * 0.1}s">
                <div class="rec-header">Recommended for You</div>
                <p><strong>${rec.name}</strong></p>
                <p>Category: ${rec.category}</p>
                <p>Price: ${rec.price}</p>
                <p>Brand: ${rec.brand}</p>
            </div>
        `;
    });
}

