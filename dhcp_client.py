#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime, timedelta

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000

def display_menu():
    print("client: Menu:")
    print("client: 1. Release")
    print("client: 2. Renew")
    print("client: 3. Quit")

def send_receive(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

    response, _ = client_socket.recvfrom(4096)
    if response:
        print("client: Received message:", response.decode())
        parsed_response = response.decode().split()
        
        if parsed_response[0] == "ACKNOWLEDGE":
            client_mac = parsed_response[1]
            assigned_ip = parsed_response[2]
            expiration_time = parsed_response[3]
            
            print(f"client: IP address {assigned_ip} assigned to client with MAC address {client_mac}.")
            print(f"client: Lease will expire at {expiration_time}.")

            # Display the menu after receiving ACKNOWLEDGE
            display_menu()
            
            while True:
                choice = input("client: Enter your choice (1-3): ")
                if choice == "1":
                    # Implement RELEASE logic
                    release_message = f"RELEASE {MAC}"
                    send_receive(release_message)
                    print("client: Release option chosen.")
                    display_menu()  # Display the menu again
                elif choice == "2":
                    # Implement RENEW logic
                    renew_message = f"RENEW {MAC}"
                    send_receive(renew_message)
                    display_menu()  # Display the menu again
                elif choice == "3":
                    print("client: Quitting...")
                    break
                else:
                    print("client: Invalid choice. Please enter 1, 2, or 3.")
    else:
        print("not workin fam")   
    print("bruh")           
    client_socket.close()

# Sending DISCOVER message
discover_message = f"DISCOVER {MAC}"
send_receive(discover_message)
