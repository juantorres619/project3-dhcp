#!/usr/bin/env python3
import socket
from datetime import datetime, timedelta
import random

# Choose a data structure to store client records
client_records = {}  # Using a dictionary to store records

# List containing all available IP addresses as strings
ip_addresses = [f"192.168.45.{i}" for i in range(1, 15)]

# Function to generate a random MAC address
def generate_random_mac():
    return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])

# Parse the client messages
def parse_message(message):
    return message.decode().split()

# Calculate response based on message
def dhcp_operation(parsed_message, client_address):
    request = parsed_message[0]
    client_mac = parsed_message[1]

    if request == "LIST":
        return "\n".join(client_records)
    elif request == "DISCOVER":
        if client_mac in client_records:
            if datetime.now() < client_records[client_mac]['timestamp']:
                # Client's lease has not expired, send ACKNOWLEDGE
                return f"ACKNOWLEDGE {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
            else:
                # Client's lease has expired, renew using the same IP
                client_records[client_mac]['timestamp'] = datetime.now() + timedelta(seconds=60)
                client_records[client_mac]['acked'] = False
                return f"OFFER {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
        else:
            # Check for available IP addresses
            if ip_addresses:
                ip_address = ip_addresses.pop(0)
                client_records[client_mac] = {'ip': ip_address, 'timestamp': datetime.now() + timedelta(seconds=60), 'acked': False}
                return f"OFFER {client_mac} {ip_address} {client_records[client_mac]['timestamp'].isoformat()}"
            else:
                # No available IP addresses, DECLINE
                return "DECLINE"
    elif request == "REQUEST":
        if client_mac in client_records and client_records[client_mac]['ip'] == parsed_message[2]:
            if datetime.now() < client_records[client_mac]['timestamp']:
                # Client's lease has not expired, send ACKNOWLEDGE
                client_records[client_mac]['acked'] = True
                return f"ACKNOWLEDGE {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
            else:
                # Client's lease has expired, send DECLINE
                return "DECLINE"
        else:
            # Client's IP address doesn't match or not in records, send DECLINE
            return "DECLINE"
    elif request == "RELEASE":
        # Implement RELEASE logic
        if client_mac in client_records:
            ip_addresses.append(client_records[client_mac]['ip'])  # Add released IP back to available IPs
            client_records[client_mac]['timestamp'] = datetime.now()  # Expire IP assignment
            client_records[client_mac]['acked'] = False  # Set acked to False
            return "RELEASED"  # Indicate to client that RELEASE is processed
        return ""  # Do nothing if client MAC address not found
    elif request == "RENEW":
        # Implement RENEW logic
        if client_mac in client_records and datetime.now() < client_records[client_mac]['timestamp']:
            client_records[client_mac]['timestamp'] = datetime.now() + timedelta(seconds=60)
            return f"RENEWED {client_mac} {client_records[client_mac]['ip']} {client_records[client_mac]['timestamp'].isoformat()}"
        else:
            return "DECLINE"

    # Return an empty string for unrecognized requests or cases where no response is needed
    return ""

# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000))
print("DHCP Server running...")

try:
    while True:
        message, client_address = server.recvfrom(4096)

        parsed_message = parse_message(message)

        response = dhcp_operation(parsed_message, client_address)

        if response:
            server.sendto(response.encode(), client_address)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
