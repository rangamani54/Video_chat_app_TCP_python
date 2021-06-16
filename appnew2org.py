import socket
import threading
import numpy as np
import cv2
import socketio
import pickle
import struct


host_name = socket.gethostname()
receiverip = socket.gethostbyname(host_name)
receiverport = 4642
st = "<sep>"
client_socket = set()

cap = cv2.VideoCapture(1)

#Server Socket
socket_address = (receiverip, receiverport)
server = socket.socket()
print("Socket created")
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind( (receiverip, receiverport) )
print("Socket binded")
server.listen(5)
print("Socket listening at IP and Port: {}".format(socket_address))

def listen(cs):
                if server:
                    data = b""
                    payload_size = struct.calcsize("Q")
                    while True:
                        while len(data) < payload_size:
                            packet = cs.recv(921600)
                            if not packet:
                                break
                            data+=packet
                        packed_msg_size=data[:payload_size]
                        data=data[payload_size:]
                        msg_size = struct.unpack("Q", packed_msg_size)[0]
                        while len(data) < msg_size:
                            data += cs.recv(921600)
                        frame=data[:msg_size]
                        data = data[msg_size:]
                        photo_frame = pickle.loads(frame)
                        #print("Waiting for client window")
                        cv2.imshow("client_video", photo_frame)
                        if cv2.waitKey(10)==13:
                            break
                    
                    cv2.destroyAllWindows()

def sending_photos():
    while True:
        for client in client_socket:
            ret, photo = cap.read()
            if ret:
                photo = pickle.dumps(photo)
                msg = struct.pack("Q", len(photo))+photo
                client.send(msg)
        
    
while True:
    client, addr = server.accept()
    print("Connection accepted for {}".format(addr))
    client_socket.add(client)
    print("client added")
    receivt = threading.Thread(target=listen, args=(client,))
    sendingt = threading.Thread(target=sending_photos)
    receivt.daemon = True
    sendingt.daemon = True
    receivt.start()
    sendingt.start()

server.close()

