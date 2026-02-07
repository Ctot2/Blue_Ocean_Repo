import time
from flask import Flask, jsonify, request, render_template
from groq import Groq
import os

app = Flask(__name__)

# In-memory food storage
food_dict = {}

# Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# -----------------------------
# FRONTEND PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# API: Add food
# -----------------------------
@app.route("/api/add_food", methods=["POST"])
def add_food():
    data = request.json
    food = data.get("food")
    seconds = data.get("seconds")

    if not food or not seconds:
        return jsonify({"error": "food and seconds required"}), 400

    food_dict[food] = time.time() + int(seconds)

    return jsonify({"message": f"{food} added"})


# -----------------------------
# API: List foods
# -----------------------------
@app.route("/api/foods")
def foods():
    return jsonify({"foods": list(food_dict.keys())})


# -----------------------------
# API: Expired foods
# -----------------------------
@app.route("/api/expired")
def expired():
    now = time.time()
    expired_list = []

    for food, exp in list(food_dict.items()):
        if now >= exp:
            expired_list.append(food)
            del food_dict[food]

    return jsonify({
        "expired": expired_list,
        "remaining": list(food_dict.keys())
    })


# -----------------------------
# API: Recipe using Groq
# -----------------------------
@app.route("/api/recipe/<food>")
def recipe(food):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": f"Give me a clear, detailed recipe using '{food}'. No intro text. If {food} isn't food, say 'Try something else'. "
            }
        ],
        temperature=1,
        max_completion_tokens=2048
    )

    text = completion.choices[0].message.content

    return jsonify({"food": food, "recipe": text})

if __name__ == "__main__":
    # Render provides a PORT environment variable. If it's not there, use 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
