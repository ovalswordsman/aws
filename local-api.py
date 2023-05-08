import requests
import json

url = "https://0s7br7ltd2.execute-api.eu-north-1.amazonaws.com/FirstStage/transactions"

# Define the data to be passed as the request body
data = {
    "transaction_id": 12345,
    "payment_mode": "card",
    "Amount": 200.0,
    "customer_id": 101
}

# Send a POST request to the API endpoint with the data as the request body
response = requests.post(url, data=json.dumps(data))

# Print the response status code and content
print(response.status_code)
print(response)
