import asyncio
import json
import websockets
import argparse  # Import the argparse module
from pynput import keyboard

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='WebSocket server for robot control.')
    parser.add_argument('--address', type=str, default='0.0.0.0:8000', help='Server address in the format ip:port')
    return parser.parse_args()

# Global variable to store the WebSocket connection
connected_clients = set()

async def send_command():
    while True:
        await asyncio.sleep(7)
        await send_control_instructions()

#This is the function that you should
async def send_control_instructions():
    print("Sending control instructions to any connected robot...")
    control_message = {
        "command": "back",
        "args": {}
    }
    for client in connected_clients:
        asyncio.create_task(client.send(json.dumps(control_message)))

async def handler(websocket, path):
    global connected_clients
    client_ip, client_port = websocket.remote_address
    print(f"New client connected: {client_ip}:{client_port}")
    connected_clients.add(websocket)
    try:
        while True:
            message = await websocket.recv()
            print(f"Received telemetry message from {client_ip}: {message}")
    finally:
        print(f"Client disconnected: {client_ip}:{client_port}")
        connected_clients.remove(websocket)

async def start_server(ip, port):
    async with websockets.serve(handler, ip, port):
        print(f"Server started on {ip}:{port}")
        await asyncio.Future()  # Run forever

async def main():
    args = parse_arguments()
    address = args.address.split(":")
    ip, port = address[0], int(address[1])
    await asyncio.gather(
        start_server(ip, port),
        send_command(),
    )

if __name__ == "__main__":
    asyncio.run(main())
