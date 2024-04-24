import requests
import logging
    
def transfer(to, amount):
    try:
        response = requests.get(f"http://localhost:8000/transfer/{to}/{amount}")
    except:
        logging.error("Unable to send request to the GWEI server.")
    else:
        print(response.text)
        return response.text

def get():
    try:
        response = requests.get("http://localhost:8000/get")
    except:
        logging.error("Unable to send request to the GWEI server.")
    else:
        print(response.json())
        return response.json()