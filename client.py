import socket
from threading import Thread
import cv2
import pickle
import struct

serverip = input("Enter the IP of server: ")
serverport = input("Enter the port of server: ")

#Client Socket
client = socket.socket()
print("Socket created")
client.connect(( serverip, int(serverport) ))
print("Connected to the server")


def receiving():
            if client:
                data = b""
                payload_size = struct.calcsize("Q")
                while True:
                    while len(data) < payload_size:
                        packet = client.recv(921600)
                        if not packet:
                            break
                        data+=packet
                    packed_msg_size=data[:payload_size]
                    data=data[payload_size:]
                    msg_size = struct.unpack("Q", packed_msg_size)[0]
                    while len(data) < msg_size:
                        data += client.recv(921600)
                    frame=data[:msg_size]
                    data = data[msg_size:]
                    photo = pickle.loads(frame)
                    #print("Waiting for server window")
                    cv2.imshow("server", photo)
                    if cv2.waitKey(10)==13:
                        break
                cv2.destroyAllWindows()

        
t = Thread( target=receiving )
t.daemon = True
t.start()


cap = cv2.VideoCapture(0)

while True:
        ret, photo = cap.read()
        if ret:
            photo = pickle.dumps(photo)
            msg = struct.pack("Q", len(photo))+photo
            client.send(msg)
            
client.close()