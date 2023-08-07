import threading
import socket

HOST = '127.0.0.1'
PORT = 50000
MAX_CLIENTS = 99

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(MAX_CLIENTS)

GROUPS = []
USERS = []

class User:
    def __init__(self, client_socket, username):
        self.client_socket = client_socket
        self.username = username


class Group:
    def __init__(self, name):
        self.name = name
        self.users = []


def create_group(group_name, user):
    not_found = True
    for group in GROUPS:
        if group.name == group_name:
            user.client_socket.sendall(f'Group already exists'.encode())
            not_found = False
    if not_found:
        GROUPS.append(Group(group_name))
        user.client_socket.sendall(f'New group chat with the name {group_name} has created successfully'.encode())


def leave_group(group_name, user, exit_mode):
    not_found = True
    for group in GROUPS:
        if group.name == group_name:
            not_found = False
            if user in group.users:
                public_message(user, group.name , f'{user.username} left the group {group.name}!')
                group.users.remove(user)
                if not exit_mode:
                    user.client_socket.sendall(f'You left the group {group.name}'.encode())
            else:
                user.client_socket.sendall(f'You are not a member of the group {group.name}'.encode())
    if not_found:
        user.client_socket.sendall(f'Group Not not_found!'.encode())


def join_group(group_name, user):
    not_found = True
    for group in GROUPS:
        if group.name == group_name:
            not_found = False
            if user not in group.users:
                group.users.append(user)
                user.client_socket.sendall(f'You joined group {group_name} successfully'.encode())
                public_message(user, group_name , f'{user.username} joined the group {group_name}')
            else:
                user.client_socket.sendall(f'You already joined the group {group_name}'.encode())
    if not_found:
        user.client_socket.sendall(f'Group Not not_found!'.encode())


def exit_server(user):
    for group in GROUPS:
        if user in group.users:
            leave_group(group.name, user, True)
    username = user.username
    USERS.remove(user)
    print(f'user {username} disconnected...')
    user.client_socket.close()  
    # user.client_socket.shutdown(socket.SHUT_RDWR)


def public_message(user, group_name, message):
    not_found = True
    for group in GROUPS:
        if group.name == group_name:
            not_found = False
            if user in group.users:
                for client in group.users:
                    if client.client_socket is not user.client_socket:
                        client.client_socket.sendall(f'[public group {group_name} from {user.username}] {message}'.encode())
            else:
                user.client_socket.sendall(f'You are not a member of the group {group_name}'.encode())
    if not_found:
        user.client_socket.sendall(f'Group Not not_found'.encode())


def private_message(user, client_name, message):
    not_found = True
    for client in USERS:
        if client.username == client_name:
            not_found = False
            client.client_socket.sendall(f'[private from {user.username}] {message}'.encode())
    if not_found:
        user.client_socket.sendall(f'Client Not not_found'.encode())
        
        
def handle(user):
    while True:
        try:
            message = user.client_socket.recv(1024)
            words = message.decode().split(" ")

            if words[0] == 'create':
                create_group(words[1], user)
                
            elif words[0] == 'join':
                join_group(words[1], user)
                
            elif words[0] == 'leave':
                leave_group(words[1], user)
                
            elif words[0] == 'groups':
                group_names = '\n'.join([group.name for group in GROUPS])
                user.client_socket.sendall(f'groups list: \n{group_names}'.encode())

            elif words[0] == 'users':
                user_names = '\n'.join([user.username for user in USERS])
                user.client_socket.sendall(f'users list: \n{user_names}'.encode())
                
            elif words[0] == 'public':
                public_message(user, words[1], ' '.join(words[2:]))

            elif words[0] == 'private':
                private_message(user, words[1], ' '.join(words[2:]))

            elif words[0] == 'exit':
                exit_server(user)
                
            else:
                user.client_socket.sendall('incorrect message'.encode())

        except Exception as e:
            print(e)
            break
 


def receive():
    while True:
        client_socket, address = server_socket.accept()
        print(f'connected with {str(address)}')
        client_socket.send('enter a username: '.encode('utf-8'))
        username = client_socket.recv(1024).decode()
        client_socket.send('connected! \n'.encode('utf-8'))
        user = User(client_socket, username)
        USERS.append(user)
        group = GROUPS[0]
        group.users.append(user)
        client_socket.send(f'you joined the group General'.encode('utf-8'))
        public_message(user,group.name, f'{username} joined the group')
        thread = threading.Thread(target=handle, args=(user,))
        thread.start()


print('Server is listening ...')
g = Group("General")
GROUPS.append(g) 
receive()