#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime

# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000

def client_menu():
    print("client: Menu: Press 1, 2, or 3")
    print("client: 1. Release")
    print("client: 2. Renew")
    print("client: 3. Quit")

def clientserver_com(message):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

    message, _ = clientSocket.recvfrom(4096)
    if message:
        parsed_response = message.decode().split()
        
        if parsed_response[0] == "ACKNOWLEDGE" or parsed_response[0] == "OFFER":
            client_mac = parsed_response[1]
            client_ip = parsed_response[2]
            client_expiration = parsed_response[3]
            
            if parsed_response[0] == "ACKNOWLEDGE":
                print(f"Received: ACKNOWLEDGE {client_mac} {client_ip} {client_expiration}")
            elif parsed_response[0] == "OFFER":
                print(f"Received: OFFER {client_mac} {client_ip} {client_expiration}")
                if client_mac == MAC:

                    request_message = f"REQUEST {MAC} {client_ip} {client_expiration}"
                    return clientserver_com(request_message)
            
            print(f"MAC address: {client_mac}")
            print(f"IP address: {client_ip}")
            print(f"Timestamp Expiration: {client_expiration}")

            client_menu()  # show menu after received message
            
            while True:
                choice = input("client: Enter your choice (1-3): ")
                if choice == "1":
                    release_message = f"RELEASE {MAC} {client_ip} {client_expiration}"
                    print("client: Releasing client IP") 
                    clientserver_com(release_message)
                    print("client: IP has been RELEASED")
                    client_menu()  
                elif choice == "2":
                    renew_message = f"RENEW {MAC} {client_ip} {client_expiration}"
                    clientserver_com(renew_message)
                    client_menu() 
                elif choice == "3":
                    print("client: Goodbye")
                    break
                else:
                    print("client: Invalid. Please choose a valid option.")

        else:
            print(f"client: Received message: {message.decode()}")  # Print received message
    else:              
        clientSocket.close()

def main():
    send_message = f"DISCOVER {MAC}"
    clientserver_com(send_message)  # Send DISCOVER message

if __name__ == "__main__":
    main()
