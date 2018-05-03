from subprocess import call
from slackclient import SlackClient
from ip_getter import get_ip
import _thread
import psutil
import time

# TODO Añadir la clave y nombre del bot
API_KEY = "API_KEY"
BOT_NAME = "BOT_NAME"
BOT_ID = "BOT_ID"
USER_LIST = {}

slack_client = SlackClient(API_KEY)

ftp_checking = False

def open_port():
    ftp_checking = True
    call(["iptables-restore", "open"])
    # Un minuto para conectar
    time.sleep(60)
    # Una vez terminado, se comprueba que haya un socket:
    has_connection = True
    while has_connection:
        has_connection = False
        list_connections = psutil.net_connections("tcp")
        # Iteramos las conexiones hasta que exista una con FTP
        for con in list_connections:
            if con.laddr[1] is 22:
                has_connection = True
                break
    call(["iptables-restore", "closed"])
    ftp_checking = False;
    
def parse_rtm(slack_info):
    response = ""
    channel = ""
    respond = False
    if slack_info and len(slack_info) > 0:
        print(slack_info)
        for msg in slack_info:
            if msg['type'] == "message":
                texto = msg.get('text')
                if texto and '<@'+BOT_ID+'>' in texto:
                    # Preparamos la respuesta
                    response = "Hola "+USER_LIST[msg.get('user')]+". La IP de casa es: http://"+get_ip()
                    channel = msg.get('channel')
                    respond = True
                    # Y activamos la apertura de los puertos:
                    if ftp_checking is False:
                        _thread.start_new_thread(open_port, ());
                    
    return response, channel, respond;

def connect_to_srv():
    # Establecemos la conexión con la API
    connect = slack_client.api_call("rtm.connect")
    # Comprobamos que se haya realizado de forma correcta
    if(connect.get('ok')):
        # Realizamos otra solicitud para coger los usuarios con su ID.
        connect = slack_client.api_call("users.list")
        users = connect.get('members')
        for user in users:
            name = user.get('name')
            USER_LIST[user.get('id')] = name
            if name == BOT_NAME:
                BOT_ID = user.get('id')
        # Iniciamos el bucle principal:
        slack_client.rtm_connect()
        slack_client.rtm_read()
        while True:
            response, channel, respond = parse_rtm(slack_client.rtm_read())
            if respond:
                slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            time.sleep(2)
    else:
        # En caso contrario, se ha producido un error
        print("Error!")
        return false
    return True
