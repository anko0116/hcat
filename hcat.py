from __future__ import print_function
import socket
import getopt
import sys
import subprocess

def help_message():
    print
    print ("anko0116's mediocre recreation of the netcat")
    print ("----------------------------------")
    print ("Usage: python hcat.py -t targetHost -p port -l -c")
    print
    sys.exit(0)
    
def recvall(sock):
    message = ""
    
    #take in all the messages
    while True:
        buffer = sock.recv(1024)
        message += buffer
        if len(buffer) < 1024:
            break
        
    return message

def check_port_range(argument):
    
    #check if the port number is within the range
    if argument < 0 and argument > 65535:
        print ("Error: port number is out of range")
        sys.exit(0)
        
def port_scanner(targetAddr):
    testSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    for i in range (1,65536):
        try:
            testSocket.connect_ex((targetAddr, i))
            #print ("Connecting to " + targetAddr, end='')
            #print (" at port", i)
            print ("Port", i, "open at", targetAddr)
        except:
            print ("didnt work")
        
def run_server(port, commandShell):
    
    #create socket, bind, listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port)) #server listens to all interfaces
    server.listen(1) 
    
    while True:
        clientSocket, clientAddr = server.accept()
        output = "[hcat]: Connection Successful!\n"
        clientSocket.sendall(output) #send connection message
        print (output, end='')
        print ("Connected from", clientAddr[0], clientAddr[1])
        
        #access to terminal
        if commandShell:
            clientSocket.sendall("[hcat]: Command Shell\n")
            clientSocket.sendall("[hcat]: $ ")
            sendMessage = ""
            
            while True:
                sendMessage = recvall(clientSocket)
                sendMessage = sendMessage.rstrip()
                response = ""
                
                try: 
                    response = subprocess.check_output(sendMessage,
                                                       stderr = subprocess.STDOUT,
                                                       shell = True)
                except:
                    response = "[hcat]: Command failed\n"
                    
                if len(response) == 0:
                    response = "[hcat]: Command executed, but no respones was generated"
                
                print(response)
                response += "\n[hcat]: $ "
                clientSocket.sendall(response)
            
            
        #sending and receiving messages

#useful resource for network packet: https://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size   
def run_client(port, targetAddr):
    
    #create client socket and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((targetAddr, port))
    
    #receive the connection message "[hcat]: Connection Successful!"
    connectionMsg = recvall(client)
    connectionMsg += recvall(client)
    print (connectionMsg, end='')
    sys.stdout.flush() 
    
    while True:
        #receive input from user and send it to server
        clientMsg = raw_input("")
        if clientMsg in ("q", "quit"):
            break
        client.send(clientMsg)
        
        #receive response
        connectionMsg = ""
        while True:
            connectionMsg += client.recv(1024)
            if len(connectionMsg) < 1024:
                break
            
        print (connectionMsg, end='')
        sys.stdout.flush()
        
def main():
    
    if len(sys.argv) == 1:
        help_message()
    
    #get the command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlp:t:cz:", ["help", "listen", "port=", "target=", "command", "scanner="])
    except getopt.GetoptError as error:
        print (str(error))
        help_message()
    
    #variables for given options and arguments
    listen = False
    port = 0
    targetAddr = ""
    commandShell = False
    portScanner = False
    
    for options, argument in opts:
        if options in ("-h", "--help"):
            help_message()
        elif options in ("-l", "--listen"):
            listen = True
        elif options in ("-p", "--port"):
            check_port_range(int(argument))
            port = int(argument)
        elif options in ("-t", "--target"):
            targetAddr = argument
        elif options in ("-c", "--command"):
            commandShell = True
        elif options in ("-z"):
            portScanner = True
            targetAddr = argument
            
    #port scanner
    if portScanner:
        port_scanner(targetAddr)
    
    #server side functions
    elif listen:
        run_server(port, commandShell)
        
    #client side functions
    elif not listen:
        run_client(port, targetAddr)
        
    print ("[hcat]: Closing hcat.py")
        
main()
    
    