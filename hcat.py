from __future__ import print_function
import socket
import getopt
import sys
import subprocess
import os

def help_message():
    print
    print ("anko0116's mediocre recreation of the netcat")
    print ("----------------------------------")
    print ("Example Usage for client: python hcat.py -t targetHost -p port")
    print ("Example Usage for server: python hcat.py -p port -l")
    print ()
    print ("     -h --help                     help menu")
    print ("     -t --target [targetHost]      target server to connect to")
    print ("     -p --port   [port]            specific port to make the connection")
    print ("     -c --command                  terminal")
    print ("     -l --listen                   listen to connections")
    print ("     -z --scanner                  scans all ports for availability")
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
            print ("Port", i, "open at", targetAddr)
        except:
            print ("didnt work")
        
def command_shell(clientSocket):
    clientSocket.sendall("[hcat]: Command Shell\n")
    clientSocket.sendall("[hcat]: " + os.getcwd() + " $ ")
    sendMessage = ""
        
    while True:
        #receive input from the client
        sendMessage = recvall(clientSocket)
        sendMessage = sendMessage.rstrip()
        response = ""
            
        #Executing commands
        try: 
            #quitting hcat
            if sendMessage in ["q", "quit", "quit()"]:
                return
                
            #changing directory in the shell
            if "cd" in sendMessage:
                command, parameter = sendMessage.split(" ", 1)
                os.chdir(parameter)                    
                    
            #create a new subprocess to run the client input on the terminal
            else:
                response = subprocess.check_output(sendMessage,
                                                   stderr = subprocess.STDOUT,
                                                   shell = True)
        except:
            response = "[hcat]: Command failed\n"
        
        print("[hcat]: Response\n" + response)
        response += "\n[hcat]: " + os.getcwd() + " $ "
        clientSocket.sendall(response)    

def run_server(port, commandShell):
    
    #create socket, bind, listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port)) #server listens to all interfaces
    server.listen(5) 
    
    #make connection
    clientSocket, clientAddr = server.accept()
    output = "[hcat]: Connection Successful!\n"
    clientSocket.sendall(output) #send connection message
    print (output, end='')
    print ("Connected from", clientAddr[0], clientAddr[1])
        
    #(-c) command shell option
    if commandShell:
        command_shell(clientSocket)
        server.close()
            
            
    #sending and receiving messages (simple connection)

#useful resource for network packet: https://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size   
def run_client(port, targetAddr):
    
    #create client socket and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((targetAddr, port))
    
    #receive the connection message "[hcat]: Connection Successful!"
    connectionMsg = recvall(client)
    connectionMsg += recvall(client)
    connectionMsg += recvall(client)
    print (connectionMsg, end='')
    sys.stdout.flush() 
    
    while True:
        #receive input from user and send it to server
        clientMsg = raw_input("")
        client.send(clientMsg)
        
        #quitting hcat
        if clientMsg in ["q", "quit", "quit()"]:
            client.close()
            break        
        
        #receive response
        connectionMsg = recvall(client)
            
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
    
    