#----------------------//CLIENT//-------------------------------

import socket
import os

def Main():
    host = '127.0.0.1'
    port = 5000

    sock = socket.socket()
    sock.connect((host, port))

    root = '.'
    fileList = {}
    for path, subdirs, files in os.walk(root):
        for name in files:
            fullFileName = os.path.join(path, name)
            if os.path.isfile(fullFileName):
                fileList[fullFileName] = os.path.getsize(fullFileName)
    print (fileList)
    sock.send(str(len(str(fileList).encode ())).encode ())
    nix = sock.recv(1024)
    sock.send(str(fileList).encode ())

    while True:
        filename = sock.recv(1024).decode()
        if (filename == "#end"):
            break
        with open(filename, 'rb') as f:
            bytesToSend = f.read(1024)
            sock.send(bytesToSend)
            while bytesToSend != b'':
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)
        print ("end")
        sock.send(b'#end')

    print ("close connection")
    sock.close ()
    

if __name__ == '__main__':
    Main()