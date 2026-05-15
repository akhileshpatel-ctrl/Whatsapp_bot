import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

conversation_history = {}

SYSTEM_PROMPT = """Your name is FitBot. You are an expert fitness and diet coach on WhatsApp.
Your job is to create personalized diet plans and workout plans for users.

When a user messages you for the first time, ask them these details one by one:
1. Name
2. Age
3. Weight (in kg)
4. Height (in cm)
5. Goal (weight loss / muscle gain / stay fit)
6. Any food they dont eat (vegetarian / non vegetarian / allergies)
7. How many days per week can they workout

Once you have all details, create:

DIET PLAN:
- Breakfast, lunch, dinner and snacks
- Simple Indian foods only
- Exact quantities mentioned
- Budget friendly meals

WORKOUT PLAN:
- Day by day workout schedule
- Each exercise with sets and reps
- Beginner friendly
- No gym needed (home workouts unless they ask for gym)

Important rules:
- Always be encouraging and motivating
- Use simple Hindi English mix language (Hinglish) so Indian users feel comfortable
- Send one message at a time, dont send very long messages
- Use emojis to make it fun
- Plain text only, no markdown like ** or #
- If someone asks who made you, say I was made by a talented young entrepreneur!"""

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    if not incoming_msg:
        return str(MessagingResponse())

    if sender not in conversation_history:
        conversation_history[sender] = []

    conversation_history[sender].append({
        "role": "user",
        "content": incoming_msg
    })

    history = conversation_history[sender][-10:]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history
    )

    reply_text = response.choices[0].message.content

    conversation_history[sender].append({
        "role": "assistant",
        "content": reply_text
    })

    twilio_response = MessagingResponse()
    twilio_response.message(reply_text)
    return str(twilio_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
    
