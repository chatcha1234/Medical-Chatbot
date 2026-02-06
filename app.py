from flask import Flask, request, jsonify
from flask_cors import CORS
from src.crew import create_crew
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    topic = data.get('topic')
    
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    
    try:
        # Initialize the crew
        # Note: In production, you might want to cache the crew agent or manage sessions
        # For now, we create a fresh crew for each request to keep it stateless
        crew = create_crew()
        
        # Kickoff with inputs
        result = crew.kickoff(inputs={'topic': topic})
        
        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
