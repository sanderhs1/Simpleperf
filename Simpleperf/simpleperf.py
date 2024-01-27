#Standard python modules
import argparse
import socket
import time
import threading
CHUNKS = 1000 # Variable to store chunk of 1000, used for bytes
seperator = "-" * 60 # Variable to store a separator I can use to print easier
# Defines a parser object, and setsup optional arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Simpleperf code')
    group = parser.add_mutually_exclusive_group(required=True) # Creates an exclusive group for client and server, so you can only run client or server not both
    group.add_argument('-c', '--client', action='store_true', help='Client mode')
    group.add_argument('-s', '--server', action='store_true', help='Server mode')
    parser.add_argument('-I', '--server_ip', type=str, default='127.0.0.1', help='IP Server')
    parser.add_argument('-b', '--bind', type=str, default='127.0.0.1', help='Binds IP')
    parser.add_argument('-p', '--server_port', type=int, default=8088,help='select port for server')
    parser.add_argument('-f', '--format', type=str, default='MB', choices=['KB', 'B', 'MB'],help='Format')
    parser.add_argument('-P', '--parallell', type=int, default=1, choices=range(1, 6), help='Parallell connections')
    parser.add_argument('-i', '--interval', type=int, help='Statistics', default=None)
    parser.add_argument("-n", "--num", dest="bytes", type=str, help="Bytes", default=0)
    parser.add_argument('-t', '--total_time', type=int, default=25,help='Duration for data sent')

    return parser.parse_args() # Returns the parsed command line arguments as tuple (finite ordered list)
# Function to parse a string value and convert it to a float value in megabytes
def parse_size(val):
    units = {"B": 1, "KB": 1024, "MB": 1048576} # Size units to value in bytes
    unit = val[-2:] # Last two characters of the size string then store it in unit
    size = int(val[:-3]) # Gets the value of the size string
    factor = units[unit] # Gets the value in bytes
    result = round(size / factor, 2) # Calculates the size in mb rounded to 2 decimals
    return result # Returns the result

# Function to handle the client
def handle_client(client_socket, client_address, args):
    # Creates variables for bytes received and starts time using time import
    bytes_received = 0
    start_time = time.time()
    # Try block that contains a loop that reads data from the client socket, until the BYE string is received or there is no more data.
    try:
        while True:
            data = client_socket.recv(CHUNKS) # receives data
            if not data:
                break
            if b'BYE' in data:
                break
            bytes_received += len(data)  # Data is stored into here

        end_time = time.time() # Finds end time
        total_duration = end_time - start_time # Calculates total time, end - start

        multipliers = {"B": 1, "KB": 1000, "MB": 1000000} # size units
        multiplier = multipliers.get(args.format, 1) # Uses the format argument for the default value
        transfer_size = bytes_received / multiplier # Finds the size of the transfer in byte
        rate_server = (transfer_size * 8) / total_duration # Finds rate server

        print(f"{'ID':<25} {'Interval':<10} {'Received':<15} {'Rate':<15}") # Prints the header above the statistics
        print(seperator) # Prints separator
        print(f"{client_address[0]}:{client_address[1]:<15} 0.0 - {int(total_duration)}       {transfer_size:0f} {args.format:<2}      {rate_server:.2f} Mbps") # uses f keys to print statistics

        client_socket.send(b"ACK: BYE") # Send BYE

    except Exception as e: # Catches exceptions and prints out the error message
        print(f"Error occurred while handling client {client_address[0]}:{client_address[1]}")
        print("Error message: ", e)
    finally: # Closes the client socket at the end of the function
        client_socket.close()

# Server function
def server(args):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creates a new server socket with specified family and type
    try:
        server_socket.bind((args.bind, args.server_port)) # Binds the socket to specified port and address
        server_socket.listen(1) # Listens for connections with a queue size of 1
    except socket.error as e:
        print("Failed to start server:", e) # If an error occurs print error message and returns
        return

    print(seperator) # Seperator
    print("A simpleperf server is listening on port", args.server_port) # Prints that server is listening on specified port
    print(seperator) # Seperator

    while True: # Accepts incoming connections and makes a new thread to handle each one
        try:
            client_socket, client_address = server_socket.accept() # Waiting for a connections, then accepts it
        except socket.error as e:
            print("Error accepting client:", e) # Prints error message, if an error occurs during accepting
            continue

        client_info = f"A simpleperf client with {client_address[0]}:{client_address[1]} is connected with {args.bind}:{args.server_port}" # Store print statement in client_info
        print(seperator) # Separator
        print(client_info) # Prints client_info
        print(seperator) # Separator
# Creates new thread to handle new client requests
        clientthread = threading.Thread(target=handle_client, args=(client_socket, client_address, args))
        clientthread.start()

# Client Function
def client(args):
    def connect(): # Function inside client called  connect
        nonlocal connects # Nonlocal is a variable declared inside nested function
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creates TCP socket
        client_socket.connect((args.server_ip, args.server_port)) # Connects client to specified IP and Port
        client_address = client_socket.getsockname() # Get client_socket address

        print(f"Simpleperf client connecting to server {args.bind}, port {args.server_port}") # Prints client connects to ip and port

        start_time = time.time() # Starts time using time import
        bytes_sent = 0 # Declares a bytes sent variable
        x=' ' # Variable to print spaces
        print(seperator) # Prints ---------------------
        print("ID" + (24*x) + "Interval" + (3*x) + "Transfer" +(8*x) +"Bandwidth") # Prints top text, with correct spacing

# If args.bytes is specified convert value to bytes, otherwise don't stop sending
        bytes_send = parse_size(args.bytes) if args.bytes else float('inf')

        stop_time = time.time() + args.total_time # Records the time connection should stop using arguments ( default 25)

        interval_start_time = start_time # Starts interval time
        interval_sent = 0 # Bytes sent in interval
        while bytes_sent < bytes_send and time.time() < stop_time: # Continue sending data until specified bytes are sent or the specified interval is over
            while time.time() - interval_start_time <= (args.interval or float('inf')): # Send data until interval is over
                if bytes_sent >= bytes_send or time.time() >= stop_time: # Break the loop if either of them are done
                    break
                data = bytes(CHUNKS) # Creates a data packet
                client_socket.sendall(data) # Sends the packet
                bytes_sent += len(data) # Adds up the total
                interval_sent += len(data) # Adds up total in interval

            if bytes_sent >= bytes_send or time.time() >= stop_time: # Break the loop if conditions are reached
                break

            duration = args.interval or (time.time() - interval_start_time) # Calculate interval time
            client_rate = (interval_sent * 8) / (duration * 1000000) # Calculate client transfer rate

            print(f"{client_address[0]}:{client_address[1]:<25} {i-args.interval}-{i:<10} {interval_sent/1000000:.1f} MB {client_rate:.2f} Mbps") # Prints statistics

            interval_sent = 0 # Resets bytes
            interval_start_time = time.time() # Record time for next interval

        client_socket.sendall(b'BYE') # Send bye to server

        while True:
            response = client_socket.recv(CHUNKS) # Recieves response from server
            if response == b"ACK: BYE":  # If the bye response is there break
                break

        client_socket.close() # Close socket

        end_time = time.time() # Takes the end time
        total_time = end_time - start_time # Calculates total time end-start
        total_size = bytes_sent / 10**6 # Calculates total size of the bytes sent in mb
        client_rate = ((bytes_sent / 10**6) * 8) / total_time # Calculates client transfer rate

        print(seperator) # Prints seperator
        print("{:<25} {:<10} {:<15} {:.2f} Mbps".format("{}:{}".format(client_address[0], client_address[1]), "0-{:.1f}".format(int(total_time)),"{:.1f} MB".format(total_size), client_rate))


    threads = [] # List to store threads
    for _ in range(args.parallell): # Loops args.parallell according to specified connections
        thread = threading.Thread(target=connect) # Creates a new thread that runs the connect function
        thread.start() # Starts the new thread
        threads.append(thread) # Adds thread to threads list
    connects = 0 # Variable to count connections
    for thread in threads: # Waits for all the threads to join
        thread.join()
        connects += 1 # Adds up connects variable

if __name__ == '__main__': # Checks if script is being executed as main program
    args = parse_arguments() # Parses the arguments using the first function
    if args.server: # If server is set
        server(args) # Run server
    elif args.client: # if client is set
        client(args) # Run Client