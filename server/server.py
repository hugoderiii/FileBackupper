# --------------------//SERVER//-----------------------
import time
import socket
import threading
import os
import ast
import io
import errno
import json

password = ''
rootPath = ''

logf = open("error.log", "w")


def RetrFile(name, sock):
    try:
        passwordCheck(sock)
        root = getPath(sock)

        fileDictionary = getFileDictionary(sock)
        if fileDictionary is None:
            return

        pullChangedFiles(sock, fileDictionary)

        fileList = getFiles(root)
        sendFileNames(sock, fileList)
        obsoleteFiles = receiveFileList(sock)
        removeObsoleteFiles(obsoleteFiles)
    except Exception as e:
        print("an exception occured. Therefore the connection was closed\nerror:"+str(e))

    sock.close()
    print('connection closed')


def passwordCheck(sock):
    clientPw = sock.recv(1024).decode()
    if password == clientPw:
        sock.send(b'OK')
    else:
        sock.send(b'CANCEL')
        raise Exception("Wrong Password Exception!")


def getPath(sock):
    folder = sock.recv(1024).decode()
    root = os.path.join(rootPath, folder)

    try:
        os.makedirs(root, exist_ok=True)
    except Exception as e:
        print("folder exists!")

    os.chdir(root)
    sock.send(b'OK')
    return root


def getFileDictionary(sock):
    dictionarySize = int(sock.recv(1024).decode())
    sock.send(b'OK')
    f = io.BytesIO(b'')
    while True:
        try:
            data = sock.recv(1024)
            f.write(data)
            if len(f.getvalue()) >= dictionarySize:
                break
        except Exception as e:
            logf.write("Failed to get file dictionary: {0}\n".format(str(e)))
            return None

    fileDictionary = ast.literal_eval(f.getvalue().decode())
    f.close()
    return fileDictionary


def pullChangedFiles(sock, fileDictionary):
    for item in fileDictionary.items():
        filename = item[0].replace("\\", "/")

        if os.path.isfile(filename):
            if os.path.getsize(filename) == item[1]:
                continue

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        if item[1] == 0:
            print("Save Empty File")
            open(filename, "w+").close()
            continue

        print("Add Or Change:", filename)
        sock.send(item[0].encode())

        totalRecv = 0
        with open(filename, 'wb') as f:
            while True:
                try:
                    data = sock.recv(1024)
                    f.write(data)
                    totalRecv += len(data)
                    if totalRecv >= item[1]:
                        break
                except Exception as e:
                    logf.write("Failed get file: {0}\n{1}\n".format(
                        filename, str(e)))
                    return

    sock.send(b"#end")
    print('files received')


def getFiles(root):
    os.chdir(root)
    fileList = []
    for path, subdirs, files in os.walk("."):
        for name in files:
            fullName = os.path.join(path, name)
            fileList.append(fullName)
        for name in subdirs:
            fullName = os.path.join(path, name)
            fileList.append(fullName)
    print("get list of all files")
    return fileList


def sendFileNames(sock, fileList):
    size = len(str(fileList).encode())
    sock.send(str(size).encode())
    sock.recv(1024)
    sock.send(str(fileList).encode())
    print("send file names")


def receiveFileList(sock):
    size = int(sock.recv(1024).decode())
    sock.send(b'OK')
    f = io.BytesIO(b'')
    while True:
        try:
            data = sock.recv(1024)
            f.write(data)
            if len(f.getvalue()) >= size:
                break
        except Exception as e:
            logf.write("Failed to get obsolete files: {0}\n".format(str(e)))
            return None

    fileList = ast.literal_eval(f.getvalue().decode())
    f.close()
    print("received file names")
    return fileList


def removeObsoleteFiles(fileList):
    # reverse iterate through list to avoid deleting non empty directories (begin with the leaves)
    for file in fileList[::-1]:
        if os.path.isfile(file):
            os.remove(file)
        else:
            os.rmdir(file)


def Main():
    print('Only works with python3! If started with python please restart with python3!')
    host = ''
    port = 5000
    global password
    global rootPath
    with open('data.json') as data_file:
        data = json.load(data_file)
        host = data["host"]
        password = data["password"]
        rootPath = data["rootPath"]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))

    s.listen(5)

    print("Server Started.")
    while True:
        c, addr = s.accept()
        print("client connected ip:<" + str(addr) + ">")
        t = threading.Thread(target=RetrFile, args=("RetrThread", c))
        t.start()
        time.sleep(1)


if __name__ == '__main__':
    Main()
