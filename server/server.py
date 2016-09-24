#--------------------//SERVER//-----------------------

import socket
import threading
import os
import ast
import io
import errno


def RetrFile(name, sock):
    #get the path
    root = "/root/Backup"
    folder = sock.recv(1024).decode()
    root = os.path.join (root, folder)

    os.makedirs(root, exist_ok=True)
	
    os.chdir(root)
    sock.send(b'OK')

    #get the fileDictionary Size
    dictionarySize = int(sock.recv(1024).decode())
    sock.send(b'OK')

    #get dictionary with files and filesize
    f = io.BytesIO(b'')
    while True:
        data = sock.recv(1024)
        f.write (data)
        if len(f.getvalue())>=dictionarySize:
            break

    fileDictionary = ast.literal_eval(f.getvalue().decode())
    f.close()


    #iterate through dictionary
    for item in fileDictionary.items():
        filename = item [0].replace ("\\","/")
        if os.path.isfile(filename):
            if os.path.getsize(filename) == item[1]:
                continue
        
        print ("Add Or Change:", filename)
        sock.send(item[0].encode())
        os.makedirs(os.path.dirname(filename),exist_ok=True)

        totalRecv = 0
        with open(filename, 'wb') as f:
            while True:
                data = sock.recv(1024)
                f.write(data)
                totalRecv +=len(data)
                if totalRecv>=item[1]:
                    break

    sock.send(b"#end")

    deleteOldFiles (fileDictionary)

    sock.close()
    print('connection closed')

def deleteOldFiles (fileDictionary):
    for path, subdirs, files in os.walk("."):
        for name in files:
            fullFileName = os.path.join(path, name)
            deleteFile = True
            for item in fileDictionary.items():
                oldFile = item[0].replace("\\","/")
                if oldFile ==fullFileName:
                    deleteFile = False
                    break
            if deleteFile:
                print ("Delete:", fullFileName.encode("utf-8", "surrogateescape"))
                os.remove(fullFileName)

def Main():
    host = '81.169.243.248'
    port = 5000


    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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