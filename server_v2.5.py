import json
import socket
import threading  # used to separate the scanning for clients?

PORT = 12345
SERVER = '127.0.0.1'  # socket.gethostname(socket.gethostname())
print(PORT)
print(SERVER)
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = '@!DSCONECT'
HEADER = 2048  # stringlength
i = 0
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
server.bind(ADDR)  # bind socket to address (conn,addr)

def handle_client(conn, addr, client_id, clients, clientalias):
    connected = True  # set status to true for this specific client.
    response = {            # response dict for client joining
        'type': 'report',
        'message': 'Connection to the Message Board Server is Successful!'
    }
    conn.sendall(json.dumps(response).encode())  # send welcome message in JSON format
    print(f'user #{client_id} connected') #debug print

    while connected:
        message_received = conn.recv(HEADER)  # start receiving messages
        message = json.loads(message_received.decode()) # Parse message to a dictionary from JSON format
        #if message:           # for debugging purposes
        #    print(message)
        command = message.get('command')
        if command == 'register':  # register user from JSON format 'command': 'register'
            duplicatefound = False
            register_name = message.get('handle')  # store from message handle to register_name from JSON format 'handle': 'handle[1]'
            for checkdupindex, aliascheck in clientalias.items():
                if aliascheck == register_name:
                    duplicatefound = True
            if duplicatefound == False:
                clientalias[client_id] = register_name # store handle in clientalias list with same index as client_id
                reg_succ = {              # response dict for client registering
                    'type': 'report',
                    'message': f'Welcome {clientalias[client_id]}!'
                }
                conn.sendall(json.dumps(reg_succ).encode()) # send a message to user that alias is registered in JSON format.
                # print(f'{clientalias[client_id]}') # For debugging purposes
            else:
                reg_fail = {
                    'type': 'report',
                    'message': f'Error: Registration failed. {register_name} already exists.' # bug fixed.
                }
                conn.sendall(json.dumps(reg_fail).encode()) # send a message to user that the alias is already taken in JSON format.

        elif command == DISCONNECT_MESSAGE:  # the disconnect message is on the client side from JSON format 'command': 'DISCONNECT_MESSGAGE'.
            print(command)
            leave_response = {
                'type': 'report',
                'message': 'Connection closed. Thank you!'
            }
            conn.sendall(json.dumps(leave_response).encode())  # send disconnect message first, since user can't receive it when already disconnected.
            conn.close()  # close for the user.
            del clientalias[client_id]  # Remove disconnected client's socket from clients list preventing the server from resending the message to that index again.
            del clients[client_id]   # Remove disconnected client's socket from clients list preventing the server from resending the message to that index again.
            connected = False  # exit loop
        elif command == 'all':  # sends message to all clients from JSON format 'command': 'all'
            messagetosend = message.get('message')  # take the message and store it in a variable
            sendtoall = {
                'type': 'public_msg',
                'to': 'all',
                'handle': clientalias[client_id],
                'message': messagetosend
            }
            all_response = {
                'type': 'report',
                'message':  'Message sent to all users.'
            }
            for id, (connA, addr) in clients.items():  # set id as key, on tuple client_id ex. (1:(conn,addr),
                # 2:(conn,addr)), and (connA, addr) as a parameter associated with key.
                if id != client_id:  # see where the key id matches in tuple client.items() depending on the (
                    # connA,addr) preventing the user to send his own message to himself.
                    connA.sendall(json.dumps(sendtoall).encode())  # send message to the socket.
                    #print(sendtoall) debugging purpose
            conn.sendall(json.dumps(all_response).encode())  # send message to sender that message is sent.

        elif command == 'msg':  # send message to one func
            issent = 0 # I changed this feel free to change 1 to True
            recipient_id = message.get('handle') # recipient
            message = message.get('message')  # split message part
            messageto1 = {
                'type': 'priv_dm',
                'from': clientalias[client_id],
                'message': message
            }
            for clientindex, alias in clientalias.items():  # set clientindex as key, and alias as the search
                # parameter in the tuple clientalias.items. Where alias matches the clientalias.items() the key is used.

                if (alias) == recipient_id:
                    recipient_socket, _ = clients[clientindex]  # match the recipientsocket with the based from where the index matches
                    recipient_socket.send(json.dumps(messageto1).encode()) # send it to that socket.
                    issent = 1  # indicates that a message is sent.
                    # print(messageto1) debugging purpose
                    if issent == 1: # I changed this feel free to change 1 to True
                        sent = {
                            'type': 'report',
                            'message': f'To {clientalias[clientindex]}: {" ".join(message)}'
                        }
                        conn.sendall(json.dumps(sent).encode())
            if issent == 0: # I changed this feel free to change 0 to False
                notsent = {
                    'type': 'report',
                    'message': 'Error: Handle or alias not found.'
                }
                conn.sendall(json.dumps(notsent).encode())
        else:
            commanderror = {
                'type': 'report',
                'message': 'Error: Command not found.'
            }
            conn.sendall(json.dumps(commanderror).encode())




def start():
    server.listen()  # start accepting people.
    print(f'Listening on port {PORT}')
    client_id = 0  # what client number is the user.
    clients = {}  # this will store the socket and address of client which makes them unique (conn,addr)
    clientalias = {}  # this will store the name of the client (originally set to Anonymous)
    while True:
        conn, addr = server.accept()
        client_id += 1  # index starts at 1 for storing
        clientalias[client_id] = 'Anonymous'  # store anonymous as name
        clients[client_id] = (conn, addr)  # store the tuple on clients[client_id]
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_id, clients, clientalias))  # start
        # threading to keep accepting clients, while able to receive and send messages)
        thread.start()
        #  print(f'[Active Connections]{threading.active_count() - 1}')   this is for debugging. (or might be important)


print('[Start]')
start()  # starts the server.
