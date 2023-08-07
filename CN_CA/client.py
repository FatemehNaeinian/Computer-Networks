import threading
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 50000))

MAX_CLIENTS = 99
BUFFER_SIZE = 4096

def Receive():
    while True:
        try:
            message = client.recv(BUFFER_SIZE).decode('utf-8')
            print(message)
        except Exception as e:
            print('Error!')
            print(e)
            client.close()
            break

def Send():
    while True:
        try:
            message = f'{input("")}'
            client.send(message.encode('utf-8'))
        except:
            print('Error!')
            break

receive_thread = threading.Thread(target=Receive)
receive_thread.start()

send_thread = threading.Thread(target=Send)
send_thread.start()

receive_thread.join()
send_thread.join()