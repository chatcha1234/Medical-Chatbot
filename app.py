from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from src.crew import create_crew
import os
import time

load_dotenv()


app = Flask(__name__)
CORS(app)

def format_history(history):
    """Helper to format conversation history for the AI."""
    if not isinstance(history, list):
        return str(history)
        
    formatted = ""
    for msg in history:
        role = "คุณหมอ" if msg.get('role') == 'assistant' else "คนไข้"
        # Avoid leaking internal thinking blocks into the AI context if possible
        content = msg.get('content', '')
        formatted += f"{role}: {content}\n"
    return formatted

@app.route('/')
def health_check():
    return "Medical Chatbot API is running correctly!"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    topic = data.get('topic')
    history = data.get('history', [])
    user_profile = data.get('user_profile', {})
    
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    
    try:
        inputs = {
            'topic': topic,
            'history': format_history(history),
            'user_profile': str(user_profile)
        }
        
        crew = create_crew(inputs)
        result = str(crew.kickoff(inputs=inputs))

        def generate():
            chunk_size = 5
            for i in range(0, len(result), chunk_size):
                yield f"data: {result[i:i+chunk_size]}\n\n"
                time.sleep(0.01)
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True, debug=False)
