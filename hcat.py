import socket
import getopt
import sys
import subprocess

def help_message():
    print
    print "anko0116's mediocre recreation of the netcat"
    print "----------------------------------"
    print "Usage: python hcat.py -t targetHost -p port -l -c"
    print
    sys.exit(0)
    
def check_port_range(argument):
    
    #check if the port number is within the range
    if argument < 0 and argument > 65535:
        print "Error: port number is out of range"
        sys.exit(0)
        
def run_server(port, commandShell):
    
    #create socket, bind, listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port)) #server listens to all interfaces
    server.listen(5) 
    
    while True:
        clientSocket, clientAddr = server.accept()
        output = "[hcat]: Connection Successful!"
        clientSocket.send(output) #send connection message
        print output
        
        #access the server's terminal
        clientSocket.send("hcat Command Shell")
        if commandShell:
            while True:
                clientSocket.send("hcat >>")
                command = clientSocket.recv(1024)
                command = command.rstrip()
                response = ""
                
                try:
                    response = subprocess.check_output(command, 
                                                       stderr = subprocess.STDOUT,
                                                       shell = True)
                except:
                    response = "Command failed"
                    
                clientSocket.send(response)
                    
                
        #loop for receiving and sending messages
        #while True:

def run_client(port, targetAddr):
    #https://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size
    #useful resource for network packet
    
    #create client socket and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((targetAddr, port))
    connectionMsg = client.recv() #receive the connection message "Connection Successful!"
    print connectionMsg
    connectionMsg = client.recv() #receive "hcat command shell"
    print connectionMsg
    
    while True:
        #receives "hcat >> "
        connectionMsg = client.recv() 
        print connectionMsg,
        
        #receive input from user and send it to server
        clientMsg = raw_input()
        client.send(clientMsg)
        
        #receive response
        print client.recv()
        
        
#Taken from "https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data"
def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data
        
        
def main():
    
    if len(sys.argv) == 1:
        help_message()
    
    #get the command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlp:t:c", ["help", "listen", "port=", "target=", "command"])
    except getopt.GetoptError as error:
        print str(error)
        help_message()
    
    #variables for given options and arguments
    listen = False
    port = 0
    targetAddr = ""
    commandShell = False
    
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
            
    #server side functions
    if listen:
        run_server(port, commandShell)
        
    #client side functions
    if not listen:
        run_client(port, targetAddr)
        
        
main()
    
    