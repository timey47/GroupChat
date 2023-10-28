from socket import *
from sys import *
from select import *

# Client needs server's contact information and its own name
if len(argv) != 4:
    print("usage:", argv[0], "<server name> <server port> <client name> ")
    exit()

# Get client's name, server's name and port
serverName = argv[1]
serverPort = int(argv[2])
clientName = argv[3]

# Create a socket
sock = socket(AF_INET, SOCK_STREAM)

# Connect to the server
sock.connect((serverName, serverPort))
print(f"{clientName} connected to server at ('{serverName}', '{serverPort}')");

# Make a file stream out of socket
sockFile = sock.makefile(mode='r')

# Make a list of inputs to watch for (keyboard and server messages)
inputSet = [stdin, sockFile]

try:
    # Keep sending and receiving messages from/to the server
    while True:

        # Wait for a message from keyboard or socket
        readableSet, _, _ = select(inputSet, [], [])

        # Message from the keyboard
        if stdin in readableSet:
            line = stdin.readline()

            # If EOF or explicit exit command, client wants to close connection
            if not line or line.strip().lower() == 'exit':
                print(f'*** {clientName} closing connection')
                break

            # Send the message to the server (with the client's name prefixed)
            sock.send(f"{clientName}: {line}".encode())

        # Message from the server (might be forwarded from other clients)
        elif sockFile in readableSet:
            line = sockFile.readline()

            # If EOF, server closed the connection or there was an issue
            if not line:
                print('*** Server closed connection')
                break

            # Display the received message
            print(line, end='')

except KeyboardInterrupt:
    print(f"\n*** {clientName} closing connection due to user interrupt")

finally:
    # Close the connection
    sockFile.close()
    sock.close()
