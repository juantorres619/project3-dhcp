#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta
import random

# Choose a data structure to store client records
client_records = {}  # Using a dictionary to store records

# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]

# Function to generate a random MAC address
def generate_random_mac():
    return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])

# Parse the client messages
def parse_message(message):
    return message.decode().split()

# Calculate response based on message
def dhcp_operation(parsed_message, clientAddress):
    request = parsed_message[0]
    client_mac = parsed_message[1]

    if request == "LIST":
        return str(client_records)
    elif request == "DISCOVER":
        print(f"server: I see that the client with MAC address {client_mac} is discovering.")
        if client_mac in client_records:
            if datetime.now() < client_records[client_mac]['timestamp']:
                # Client's lease has not expired, send ACKNOWLEDGE
                print(f"server: I assigned IP address {client_records[client_mac]['ip']} to client with MAC address {client_mac}.")
                return f"ACKNOWLEDGE {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
            else:
                # Client's lease has expired, renew using the same IP
                client_records[client_mac]['timestamp'] = datetime.now() + timedelta(seconds=60)
                client_records[client_mac]['acked'] = False
                print(f"server: Client with MAC address {client_mac} renewed IP address {client_records[client_mac]['ip']}.")
                return f"OFFER {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
        else:
            # Check for available IP addresses
            if ip_addresses:
                ip_address = ip_addresses.pop(0)
                client_records[client_mac] = {'ip': ip_address, 'timestamp': datetime.now() + timedelta(seconds=60), 'acked': False}
                print(f"server: I assigned IP address {ip_address} to client with MAC address {client_mac}.")
                return f"OFFER {client_mac} {ip_address} {client_records[client_mac]['timestamp'].isoformat()}"
            else:
                # No available IP addresses, DECLINE
                print("server: No available IP addresses.")
                return "DECLINE"
    elif request == "REQUEST":
        print(f"server: REQUEST received")
        if client_mac in client_records and client_records[client_mac]['ip'] == parsed_message[2]:
            if datetime.now() < client_records[client_mac]['timestamp']:
                # Client's lease has not expired, send ACKNOWLEDGE
                client_records[client_mac]['acked'] = True
                print(f"server: Client with MAC address {client_mac} requested IP address {client_records[client_mac]['ip']} which is already assigned.")
                return f"ACKNOWLEDGE {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
            else:
                # Client's lease has expired, send DECLINE
                print(f"server: Client with MAC address {client_mac} requested IP address {client_records[client_mac]['ip']} which has expired.")
                return "DECLINE"
        else:
            # Client's IP address doesn't match or not in records, send DECLINE
            print(f"server: Client with MAC address {client_mac} requested invalid or unassigned IP address.")
            return "DECLINE"
    elif request == "RELEASE":
        print("server: RELEASE received")
        if client_mac in client_records:
            print(client_mac)
            client_records[client_mac]['timestamp'] = datetime.now()
            client_records[client_mac]['acked'] = False
            # Display the client's IP address and port number
            print(f"server: Released IP address {client_records[client_mac]['ip']} assigned to client {client_mac} with port number {clientAddress[1]}.")
            return ""
        else:
            # If the client's MAC address is not found in the records, do nothing
            print("server: Client's MAC address not found in records.")
            return "DECLINE"
    elif request == "RENEW":
        print("server: RENEW received")
        if client_mac in client_records: #and datetime.now() < client_records[client_mac]['timestamp']
            client_records[client_mac]['timestamp'] = datetime.now() + timedelta(seconds=60)
            print(f"server: Client with MAC address {client_mac} renewed IP address {client_records[client_mac]['ip']}.")
            return f"RENEWED {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
        else:
            return "DECLINE"

    return ""

# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000))
print("server: DHCP Server running...")

try:
    while True:
        message, clientAddress = server.recvfrom(4096)

        parsed_message = parse_message(message)

        response = dhcp_operation(parsed_message, clientAddress)

        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
