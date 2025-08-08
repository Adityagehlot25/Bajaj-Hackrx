import requests
try:
    r = requests.get("http://localhost:8000/api/v1/hackrx/health")
    print("Server is running:", r.json())
except:
    print("Server is not running - start with: python start_hackrx_server.py")
