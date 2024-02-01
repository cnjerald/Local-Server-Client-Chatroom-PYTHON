import json
import socket
import threading

HEADER = 2048
client = ''
isconnected = False
DISCONNECT_MESSGAGE = "@!DSCONECT"  # acts as a key

def helpcommand():
    print("Command 1. [/join <server_ip_add> <portNum>] Description: Joins a server using valid IP and Port")
    print("Command 2. [/leave] Description: Leaves the server")
    print("Command 3. [/register <handle>] Description: Register a username or alias")
    print("Command 4. [/all <message>] Description: Send a public message to ALL users in the server")
    print("Command 5. [/msg <handle> <message>] Description: Send a private message to <alias> in the server")

def receive_messages():
    while isconnected:
        # print("Waiting for message...")  # FOR DEBUGGING
        message = client.recv(HEADER)
        if not message:
            print("no message")
            break
        response = json.loads(message.decode())  # Parse message to a dictionary
        type = response.get('type')
        if type == 'priv_dm': # if message type received is private message
            from_who = response.get('from') ## from who
            message = ' '.join(response.get('message')) ## message part.
            print(f"[From {from_who} to You]: {message}") # print out message
        elif type == 'public_msg':
            from_who = response.get('handle')
            message = ' '.join(response.get('message'))
            print(f"From {from_who} to Everyone: {message}") # print out message
        elif type == 'report':  # if there is a message from server
            message = response.get('message')
            print(message)  # print the message.
        else:
            print('Received message')
    client.close()



print("Input a command [Input /? for all commands] ")
command = 0  # this is just to prevent warnings.
while command!='/exit':
    while not isconnected:
        command = input()
        if command == "/?":
            helpcommand() # call help command function
        else:
            if "/join" in command:
                if (len(command.split()) != 3):
                    print("Error: command parameter conditions is not met")
                else:
                    joinuser = command.split()
                    join = {
                        'command': 'join',
                        'server': joinuser[1],
                        'port': int(joinuser[2])
                    }
                    if len(joinuser[1]) != 9 or len(joinuser[2]) != 5:
                        # (This will work as long as input is 127.0.0.1 12345) but changing server or port might break it.
                        print("Error command parameters do not match or is not allowed.")
                    else:
                        SERVER = join['server']  # use SERVER
                        PORT = join['port'] # use PORT
                        try:
                            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # this must be placed here
                            # to recreate the socket when the user leaves so that user can rejoin.
                            ADDR = (SERVER, PORT)
                            client.connect(ADDR)
                            print("Connecting to server...")
                            isconnected = True  # is connected set to true
                            if isconnected:
                                print("Connection established") # check if connection is established
                        except ConnectionRefusedError:  # some error handling.... below
                            isconnected = False
                            print("Error: Connection to the Message board Server has failed! Please check IP Address and Port Number")
                        except TimeoutError:
                            isconnected = False
                            print("Error: Connection timeout")
                        except socket.gaierror as e:
                            isconnected = False
                            print("Error: Connection to the Message board Server has failed! Please check IP Address and Port Number")
            elif "/register" in command or "/all" in command or "/msg" in command:
                print("Alert: You are not connected to a server.")
            elif "/leave" in command:
                print("Error: Disconnection Failed, Please connect to a server first")
            elif "/exit" in command:
                print("End of Line...")
                isconnected = False
            else:
                print("Error: Command not found")

    if isconnected == True:
        receive_thread = threading.Thread(target=receive_messages)  # start threading, so that the user can input, while
        # receiving messages
        receive_thread.start()

    try:
        while isconnected == True:
            command = input()
            if "/register" in command: #client sends command to register username on server
                handle = command.split() # ask for username
                if len(handle) == 2:
                    register = {
                        'command': 'register',
                        'handle': handle[1]
                    }
                    client.sendall(json.dumps(register).encode()) # client sends register command to server in JSON format
                else:
                    print("Error: Incorrect Format")
            elif "/leave" in command:
                leave = {
                    'command': DISCONNECT_MESSGAGE
                }
                client.sendall(json.dumps(leave).encode())  # client sends leave command to server in JSON format
                isconnected = False
            elif "/all" in command:
                all_message = command.split()
                if len(all_message) > 1:
                    all = {
                        'command': 'all',
                        'message': all_message[1:]
                    }
                    client.sendall(json.dumps(all).encode()) # client sends all command to server in JSON format
                else:
                    print("Error: Incorrect Format")
            elif "/msg" in command:
                message_dm = command.split()
                if len(message_dm) > 2:
                    message = {
                        'command': 'msg',
                        'handle': message_dm[1],
                        'message': message_dm[2:]
                    }
                    client.sendall(json.dumps(message).encode()) # client sends all command to server in JSON format
                else:
                    print("Error: Incorrect Format")
            elif "/join" in command:
                print("Alert: Already in the server")
            else:
                print("Error: Command not found")

    except KeyboardInterrupt:
        print("Keyboard Interrupt: Disconnecting...")
        leave = {
            'command': DISCONNECT_MESSGAGE
        }
        isconnected = False
        client.sendall(json.dumps(leave).encode())  # client sends leave command to server in JSON format
    except Exception as e:
        print(f"Error: {e}")
        leave = {
            'command': DISCONNECT_MESSGAGE
        }
        isconnected = False
        client.sendall(json.dumps(leave).encode())  # client sends leave command to server in JSON format



