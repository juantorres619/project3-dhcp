import socket
import random
import time

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000

# Number of DISCOVER messages to send
NUM_DISCOVERS = 14

def generate_random_mac():
    return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])

def send_discover():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1)  # Set timeout to 1 second
    mac_address = generate_random_mac()
    discover_message = f"DISCOVER {mac_address}"
    client_socket.sendto(discover_message.encode(), (SERVER_IP, SERVER_PORT))
    print(f"Attacker: Sent DISCOVER message with MAC address {mac_address}")
    try:
        response, _ = client_socket.recvfrom(4096)
        print("Attacker: Received response:", response.decode())
    except socket.timeout:
        print("Attacker: No response received within the timeout period")
    client_socket.close()

def main():
    for _ in range(NUM_DISCOVERS):
        send_discover()
        time.sleep(0.5)  # Add a small delay between each DISCOVER message

if __name__ == "__main__":
    main()