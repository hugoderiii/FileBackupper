#--------------------//SERVER//-----------------------

import socket
import threading
import os
import ast
import io

def RetrFile(name, sock):
    length = int(sock.recv(1024).decode())
    sock.send(b'hallo')
    print (length)
    #get dictionary with files and filesize
    f = io.BytesIO(b'')
    while len(f.getvalue()) < length:
        data = sock.recv(1024)
        f.write (data)
        print (len(f.getvalue()))

    print ("hallo3")
    fileDictionary = ast.literal_eval(f.getvalue().decode())
    print (fileDictionary)

    #iterate through dictionary
    for item in fileDictionary.items():
        if os.path.isfile(item[0]):
            if os.path.getsize(item[0]) == item[1]:
                continue
        
        sock.send(item[0].encode())
        with open(item[0], 'wb') as f:
            while True:
                data = sock.recv(1024)
                if data == b'#end':
                    break
                f.write(data)

        f.close()
    sock.send(b"#end")

    sock.close()
    print('connection closed')

def Main():
    host = '127.0.0.1'
    port = 5000


    s = socket.socket()
    s.bind((host,port))

    s.listen(5)

    print ("Server Started.")
    while True:
        c, addr = s.accept()
        print ("client connected ip:<" + str(addr) + ">")
        t = threading.Thread(target=RetrFile, args=("RetrThread", c))
        t.start()
         
    s.close()

if __name__ == '__main__':
    Main()