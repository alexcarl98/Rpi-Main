import requests

def is_connected():
    try:
        requests.head("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False