import requests
import logging
    
def transfer(to, amount):
    try:
        response = requests.get(f"https://gwei-server.onrender.com/transfer/{to}/{amount}")
    except:
        logging.error("Unable to send request to the GWEI server.")
    else:
        print(response.text)
        return response.text

def get():
    try:
        response = requests.get("https://gwei-server.onrender.com/get")
    except:
        logging.error("Unable to send request to the GWEI server.")
    else:
        print(response.json())
        return response.json()