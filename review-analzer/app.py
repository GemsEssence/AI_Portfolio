from flask import Flask, render_template, request, jsonify
from models.ai_model import analyze_review

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    review_text = data.get("review", "")

    if not review_text:
        return jsonify({"error": "Review text is required"}), 400

    result = analyze_review(review_text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
