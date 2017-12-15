#----------------------//CLIENT//-------------------------------

import socket
import os
import sys
import json
import io
import ast

password = ''

def Main():

	if (len(sys.argv)==1):
		directoriesList = []
		with open("directories.list") as f:
			directoriesList = f.read().splitlines()
	else:
		directoriesList = sys.argv[1:]

	host = ''
	global password
	with open('data.json') as data_file:    
		data = json.load(data_file)
		host = data["host"]
		password = data["password"]


	port = 5000
	for directory in directoriesList:
		openConnection (host, port, directory)

def openConnection (host, port, root):
	sock = socket.socket()
	sock.connect((host, port))
	fileDictionary = getFileDictionary (root)

	sendPassword (sock, password)
	sendBaseFolder (sock,root)
	sendDictionary (sock, fileDictionary)
	sendFiles(sock)

	serverFiles = receiveFileList (sock)
	obsoleteFiles = checkServerFilesExist (serverFiles)
	print (obsoleteFiles)
	sendFileNames (sock, obsoleteFiles)

	print ("close connection")
	sock.close ()

def getFileDictionary (root):
	os.chdir(root)
	fileDictionary = {}
	for path, subdirs, files in os.walk("."):
		for name in files:
			fullFileName = os.path.join(path, name)
			if os.path.isfile(fullFileName):
				fileDictionary[fullFileName] = os.path.getsize(fullFileName)
	print ("get file dictionary")
	return fileDictionary

def sendPassword (sock, password):
	sock.send(password.encode())
	answer = sock.recv(1024).decode()
	if (answer =="CANCEL"):
		sock.close ()
		print ("close because of wrong password")
		return None
	print ("send password")

def sendBaseFolder (sock,root):
	sock.send(os.path.basename(os.path.normpath(root)).encode())
	sock.recv(1024)
	print ("send basefolder")

def sendDictionary (sock,fileDictionary):
	dictionarySize = len(str(fileDictionary).encode ())
	sock.send(str(dictionarySize).encode ())
	sock.recv(1024)
	sock.send(str(fileDictionary).encode ())
	print ("send dictionary")

def sendFiles (sock):
	while True:
		filename = sock.recv(1024).decode()
		if (filename == "#end"):
			break

		print ("Send File: ", filename.encode('utf-8'))
		with open(filename, 'rb') as f:
			bytesToSend = f.read(1024)
			sock.send(bytesToSend)
			while bytesToSend != b'':
				bytesToSend = f.read(1024)
				sock.send(bytesToSend)
	print ("send files")

def receiveFileList (sock):
	size = int(sock.recv(1024).decode())
	sock.send(b'OK')
	f = io.BytesIO(b'')
	while True:
		try:
			data = sock.recv(1024)
			f.write (data)
			if len(f.getvalue())>=size:
				break
		except Exception as e:
			logf.write("Failed to get file list: {0}\n".format( str(e)))
			return None;

	fileList = ast.literal_eval(f.getvalue().decode())
	f.close()
	print ("received file list")
	return fileList

def checkServerFilesExist (fileList):
	obsoleteFiles = []
	for fileName in fileList:
		if not os.path.exists (fileName):
			obsoleteFiles.append (fileName)
	print ("found all obsolete files")
	return obsoleteFiles



def sendFileNames (sock,fileList):
	size = len(str(fileList).encode ())
	sock.send(str(size).encode ())
	sock.recv(1024)
	sock.send(str(fileList).encode ())
	print ("have send file names")

if __name__ == '__main__':
  Main()