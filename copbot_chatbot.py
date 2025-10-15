import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
import docx
from fuzzywuzzy import process
from deep_translator import GoogleTranslator
from langdetect import detect

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load police-related Q&A from a document
def load_police_data(doc_path):
    qa_pairs = {}
    try:
        doc = docx.Document(doc_path)
        question = None
        for para in doc.paragraphs:
            text = para.text.strip()
            if text.startswith("Q:"):
                question = text[2:].strip().lower()
            elif text.startswith("A:") and question:
                answer = text[2:].strip()
                qa_pairs[question] = answer
                question = None
        print("✅ Document Loaded Successfully:", len(qa_pairs), "Q&A pairs found.")
    except Exception as e:
        print("❌ Error loading document:", str(e))
    return qa_pairs

# Load document on startup
doc_path = "police_data.docx"
police_data = load_police_data(doc_path)

# Function to find the best match for user queries
def get_best_match(user_input, questions):
    best_match, score = process.extractOne(user_input, questions)
    return best_match if score > 50 else None  # Adjust threshold for better matching

# Handle real-time messages using WebSockets
@socketio.on("message")
def handle_message(user_input):
    print(f"Received message: {user_input}")

    # Detect the user's language
    user_lang = detect(user_input)

    # Translate user input to English
    translated_text = GoogleTranslator(source=user_lang, target="en").translate(user_input).lower()

    # Find the best match in English
    best_match = get_best_match(translated_text, police_data.keys())

    # Get the response in English
    response = (
        police_data.get(best_match, "I'm sorry, I couldn't find relevant information.")
        if best_match
        else "I'm sorry, I couldn't find relevant information."
    )

    # Translate response back to the user's language
    final_response = GoogleTranslator(source="en", target=user_lang).translate(response)

    print(f"Bot Response: {final_response}")
    socketio.send(final_response)  # Send response back to the client

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
