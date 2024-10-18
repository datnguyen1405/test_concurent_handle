from flask import Flask, request, jsonify, Response, session
import time
import threading
import uuid
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Track the number of active users
active_users = set()
lock = threading.Lock()

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    logging.debug(f"Index accessed by user: {session['user_id']}")
    return app.send_static_file('index.html')

@app.route('/get_user_id')
def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    logging.debug(f"User ID requested: {session['user_id']}")
    return jsonify({"user_id": session['user_id']})

@app.route('/process', methods=['POST'])
def process_number():
    data = request.get_json()
    number = data.get('number')

    # Simulate processing
    time.sleep(1)  # Step 1: Power with 2
    result = int(number) ** 2
    
    time.sleep(1)  # Step 2: Multiply result with 10
    final_result = result * 10

    return jsonify({"result": final_result})

@app.route('/user_count')
def user_count():
    def generate(user_id):
        with lock:
            if user_id not in active_users:
                active_users.add(user_id)
                logging.debug(f"New user added: {user_id}. Total users: {len(active_users)}")
        
        try:
            while True:
                with lock:
                    count = len(active_users)
                logging.debug(f"Sending count: {count}")
                yield f"data: {count}\n\n"
                time.sleep(1)  # Update frequency
        except GeneratorExit:
            # This block will be executed when the client disconnects
            logging.debug(f"Client disconnected: {user_id}")
            raise  # Re-raise the GeneratorExit exception
        finally:
            with lock:
                active_users.discard(user_id)
                logging.debug(f"User removed: {user_id}. Total users: {len(active_users)}")

    # Get the user_id from the session while we're still in the request context
    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id

    return Response(generate(user_id), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
