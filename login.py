import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from letta_client import Letta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages and sessions

# Letta API details
LETTA_API_URL = "https://api.letta.com/v1/agents"  # Correct API endpoint for creating agents
LETTA_API_KEY = "ZjVlNWM5YzAtZWE3Yi00NWUzLTg5ZGEtZDMxZjNkYTA0YzZhOmI4ZDg3MTUzLWFlMzktNGUwZS04MDY0LTM3MmJkMjllODFjZA=="  # Replace with your Letta API key

# Load users from JSON file
def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save users to JSON file
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

# Load existing users from the JSON file
users_db = load_users()

# Check if agent exists for the user
def get_agent_for_user(username):
    headers = {'Authorization': f'Bearer {LETTA_API_KEY}'}
    response = requests.get(LETTA_API_URL + '?name=' + username, headers=headers)

    if response.status_code == 200:
        agents = response.json()
        if len(agents) >= 1:
            return agents[0]
    return None  # No agent found

# Create a new agent for the user using the requests library
def create_agent_for_user(username):
    headers = {
        'Authorization': f'Bearer {LETTA_API_KEY}',  # Ensure this is your correct API key
        'Content-Type': 'application/json'
    }

    print(f"Headers being sent: {headers}")
    
    # Define the body of the POST request
    agent_data = {
        'name': username,
        'from_template':"UCM_Financial_Literacy:latest"
    }

    # Send a POST request to the Letta API to create the agent
    create_response = requests.post(LETTA_API_URL, json=agent_data, headers=headers)
    print(create_response.text)

    # Check the response
    if create_response.status_code == 201:
        return create_response.json()  # Return the created agent's data
    else:
        print(f"Failed to create agent: {create_response.status_code}")
        print(create_response.json())  # Print the response for more details
        return None  # Failed to create agent

@app.route('/message', methods=['POST'])
def create_message():
    # We can assume the user is logged in and the agentid is available in the session
    agent_id = session['agentid']
    
    print('hi')
    # Get the message from the form submission
    payload = request.get_json()
    message = payload['message']

    # Check if a message was provided
    if not message:
        flash("Please enter a message.", 'danger')
        return "failed"

    # Prepare headers and the message data for the request
    headers = {
        'Authorization': f'Bearer {LETTA_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Define the message body
    message_data = {
        "messages": [{
            "role": "user",
            "content": message,
        }],
    }

    # Send the POST request to the Letta API to send the message to the agent
    message_url = f"{LETTA_API_URL}/{agent_id}/messages"  # Adjust URL for sending messages if needed
    response = requests.post(message_url, json=message_data, headers=headers)

    if response.status_code == 200:
        # Successful message send
        flash("Message sent successfully.", 'success')
        return response.json()
    else:
        # Handle failure
        flash("Failed to send message. Please try again.", 'danger')
        return response.json()
    

# Home route for login page
@app.route('/')
def home():
    return render_template('login.html')

# Route for login handling
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if the username exists and the password is correct
    if username in users_db and users_db[username] == password:
        # Check if an agent exists for the user in Letta
        agent = get_agent_for_user(username)
        if not agent:
            # If no agent exists, create a new one
            agent = create_agent_for_user(username)

        if agent:
            # Store the agent information in the session
            session['username'] = username
            print("agent value is " + str(agent))
            session['agentid'] = agent['id']  # Store agent information in session (optional)
            # flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('user_page', username=username))
        else:
            flash("Failed to create or retrieve agent. Please try again.", 'danger')
            return redirect(url_for('home'))
    else:
        flash("Invalid username or password. Please try again.", 'danger')
        return redirect(url_for('home'))

# Route to render a personalized user page with a greeting
@app.route('/user/<username>')
def user_page(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('home'))  # If the session username doesn't match, redirect to login

    # Greet the user by their username
    return render_template('userPage.html', username=username)

# Route to create an account
@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users_db:
            flash("Username already exists. Please choose another one.", 'danger')
            return redirect(url_for('create_account'))

        # Add new username and password to the mock database
        users_db[username] = password
        save_users(users_db)  # Save the updated users list to the file

        flash("Account created successfully. You can now log in.", 'success')
        return redirect(url_for('home'))

    return render_template('createAccount.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    session.pop('agent', None)  # Remove agent from session if exists
    return redirect(url_for('home'))  # Redirect back to login page

if __name__ == '__main__':
    app.run(debug=True)
