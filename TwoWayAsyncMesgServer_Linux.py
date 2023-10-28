from socket import *
from sys import *
from select import *

# Server needs the port number to listen on
if len(argv) != 2:
    print('usage:', argv[0], '<port>')
    exit()

serverPort = int(argv[1])

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', serverPort))
serverSock.listen()
print('Server is ready to receive clients ...')

# List to store active client sockets
clients = []

# Make a list of inputs to watch for (initially just the server socket)
inputSet = [serverSock, stdin]

try:
    while True:
        readableSet, _, _ = select(inputSet, [], [])

        # New client trying to connect
        if serverSock in readableSet:
            clientSock, clientAddr = serverSock.accept()
            print('Connected to a client at', clientAddr)
            clients.append(clientSock)
            inputSet.append(clientSock)  # Add the new client socket to input set

        # Message from the keyboard (server's input)
        elif stdin in readableSet:
            line = stdin.readline()
            if not line:
                print('*** Server shutting down')
                break
            # Broadcast the server message to all clients
            for client in clients:
                client.send(f"Server: {line}".encode())

        else:
            # Message from one of the clients
            for clientSock in readableSet:
                data = clientSock.recv(1024)
                
                # If client sends null message or disconnects
                if not data:
                    print(f"*** Client {clientSock.getpeername()} closed connection")
                    clients.remove(clientSock)
                    inputSet.remove(clientSock)
                    clientSock.close()
                    continue
                
                # Forward the message from this client to all other clients
                for otherClient in clients:
                    if otherClient != clientSock:
                        otherClient.send(data)

except KeyboardInterrupt:
    print("\n*** Server shutting down")
    
finally:
    for client in clients:
        client.close()
    serverSock.close()
