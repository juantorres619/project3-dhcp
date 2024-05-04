#!/usr/bin/env python3
import uuid
import socket


# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000

def send_discover():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.settimeout(1)  # Set timeout to 1 second
    message = f"LIST {MAC}"
    clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
    print(f"Admin: Sent LIST message with MAC address {MAC}")
    try:
        response, _ = clientSocket.recvfrom(4096)
        records = {}
        records = response.decode().split('\n')
        print(records)
    except socket.timeout:
        print("ADMIN: No response received within the timeout period")
    clientSocket.close()

def main():
        send_discover()
        

if __name__ == "__main__":
    main()


