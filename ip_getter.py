import requests
from slackclient import SlackClient;

def get_ip():
    request = requests.get("http://myexternalip.com/raw");
    
    if request.status_code == 200:
        print("IP: "+request.text);
    else:
        print("Error, HTTP code: "+request.status_code);
    
    return request.text;
