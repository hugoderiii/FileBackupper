#----------------------//CLIENT//-------------------------------

import socket
import os
import sys
import json

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

	print ("close connection")
	sock.close ()


def sendPassword (sock, password):
	sock.send(password.encode())
	answer = sock.recv(1024).decode()
	if (answer =="CANCEL"):
		sock.close ()
		print ("close because of wrong password")
		return None

def sendBaseFolder (sock,root):
	sock.send(os.path.basename(os.path.normpath(root)).encode())
	sock.recv(1024)

def sendDictionary (sock,fileDictionary):
	dictionarySize = len(str(fileDictionary).encode ())
	sock.send(str(dictionarySize).encode ())
	sock.recv(1024)
	sock.send(str(fileDictionary).encode ())

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

def getFileDictionary (root):
	os.chdir(root)
	fileDictionary = {}
	for path, subdirs, files in os.walk("."):
		for name in files:
			fullFileName = os.path.join(path, name)
			if os.path.isfile(fullFileName):
				fileDictionary[fullFileName] = os.path.getsize(fullFileName)
	return fileDictionary

if __name__ == '__main__':
  Main()