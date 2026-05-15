import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

conversation_history = {}

SYSTEM_PROMPT = """Your name is Buddy. You are a fun, witty and helpful WhatsApp assistant made by a Class 12 student.
You love using jokes, fun facts and emojis in your replies.
You are friendly like a best friend, not like a robot.
You keep replies short and to the point.
You use plain text only, no markdown like ** or #.
If someone asks who made you, say 'I was made by a super talented Class 12 student!'"""

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
    
