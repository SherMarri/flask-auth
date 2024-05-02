"""Simulates calls to API requesting password reset"""

import requests
import json
import time

customers_file = "/home/sher/Downloads/customer_export.json/customer_export.json"

# Read JSONL
with open(customers_file, "r") as f:
    customers = [json.loads(line) for line in f]


max_requests = 120
start = time.time()
for i in range(max_requests):
    customer = customers[i]
    email = customer["email"]
    url = "http://localhost:5000/auth/forgot_password"
    payload = json.dumps({"email": email})
    headers = {
        "Content-Type": "application/json",
        "X-Client-Version": "2.1.0",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(f"Request {i+1} of {max_requests} sent to {url} with email {email}")
    else:
        print(
            f"Request {i+1} of {max_requests} failed with status code {response.status_code}"
        )
    print("")

end = time.time()
print(f"Time elapsed: {end - start}")
