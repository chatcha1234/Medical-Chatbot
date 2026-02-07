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

import json
import threading
import queue
import sys

class ThinkingCallback:
    def __init__(self, q):
        self.q = q
    
    def __call__(self, step):
        try:
            # Capture the agent's thought process
            content = str(step)
            agent_name = "Agent"

            # CrewAI 1.0+ structures
            if hasattr(step, 'thought') and step.thought:
                content = step.thought
            elif hasattr(step, 'log') and step.log:
                content = step.log
            
            if hasattr(step, 'agent'):
                agent_name = step.agent

            log_entry = {
                "type": "thinking",
                "agent": agent_name,
                "content": content
            }
            print(f">>> Log: {agent_name} is thinking...", file=sys.stdout, flush=True)
            self.q.put(json.dumps(log_entry))
        except Exception as e:
            print(f"!!! Callback Error: {e}", file=sys.stdout, flush=True)

class TaskCallback:
    def __init__(self, q):
        self.q = q
        
    def __call__(self, task_output):
        try:
            log_entry = {
                "type": "thinking",
                "agent": "System",
                "content": f"Task Completed: {task_output.description[:100]}..."
            }
            self.q.put(json.dumps(log_entry))
        except Exception:
            pass

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
        
        q = queue.Queue()
        callback = ThinkingCallback(q)
        t_callback = TaskCallback(q)

        def run_crew():
            try:
                print("DEBUG: Creating crew with callbacks", flush=True)
                crew = create_crew(inputs, step_callback=callback)
                # Task callbacks need to be assigned to each task
                for task in crew.tasks:
                    task.callback = t_callback

                print("DEBUG: Kickoff starting...", flush=True)
                result = str(crew.kickoff(inputs=inputs))
                print(f"DEBUG: Kickoff finished. Result length: {len(result)}", flush=True)
                # Send the final answer
                answer_entry = {
                    "type": "answer",
                    "content": result
                }
                q.put(json.dumps(answer_entry))
            except Exception as e:
                q.put(json.dumps({"type": "error", "content": str(e)}))
            finally:
                q.put("[DONE]")

        # Start crew in a background thread
        print("DEBUG: Starting Crew thread...", flush=True)
        threading.Thread(target=run_crew).start()

        def generate():
            print("DEBUG: SSE generator started", flush=True)
            while True:
                item = q.get()
                if item == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                yield f"data: {item}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True, debug=False)
