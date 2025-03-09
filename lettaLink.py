import requests
import json

LETTA_API_URL = "https://api.letta.com/v1/agents"  # Correct API endpoint for creating agents
API_KEY = "ZjVlNWM5YzAtZWE3Yi00NWUzLTg5ZGEtZDMxZjNkYTA0YzZhOmI4ZDg3MTUzLWFlMzktNGUwZS04MDY0LTM3MmJkMjllODFjZA"  # API key for authentication

# Create a function to interact with the Letta API
def send_request(endpoint, method="GET", data=None):
    url = f"{LETTA_API_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, data=json.dumps(data))
    elif method == "PUT":
        response = requests.put(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")

def create_user_agent(username):
    agent_data = {
        "username": username,
        "identity": f"{username}_identity"
    }

    response = send_request("agents", method="POST", data=agent_data)  # Correct POST for agent creation
    return response  # Return agent data upon success

# Example usage
username = "foxfire"
response = create_user_agent(username)
print(response)
