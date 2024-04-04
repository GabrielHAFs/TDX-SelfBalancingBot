from PySide2.QtWidgets import QApplication

from face import FaceWidget

import sys
import asyncio
import argparse  # Import the argparse module
import threading

test_mode = False

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='WebSocket server for robot control.')
    parser.add_argument('--address', type=str, default='0.0.0.0:8000', help='Server address in the format ip:port')
    return parser.parse_args()

def run_gui():
    app = QApplication(sys.argv)
    face_widget = FaceWidget()

    if test_mode:  # Assuming test_mode comes from parsed arguments
        face_widget.show()
    else:
        face_widget.showFullScreen()

    sys.exit(app.exec_())

async def main():
    args = parse_arguments()
    address = args.address.split(":")
    ip, port = address[0], int(address[1])

    # server = aServer()

    # asyncio.ensure_future(server.handler())
    # asyncio.ensure_future(server.start_server("127.0.0.1", 9000))

    app = QApplication(sys.argv)
    face_widget = FaceWidget()

    if test_mode:
        face_widget.show()
    else:
        face_widget.showFullScreen()

    client = face_widget
    client.startConnection(f"ws://{ip}:{port}")
    # Example sending a message
    client.send_message("Hello from client!")
        
    sys.exit(app.exec_())

if __name__ == "__main__":
    asyncio.run(main())