#--------------------//SERVER//-----------------------
import time
import socket
import threading
import os
import ast
import io
import errno
import json

password = ''

logf = open("error.log", "w")

def RetrFile(name, sock):
	passwordCheck (sock)
	getPath (sock)
	dictionarySize = getDictionarySize (sock)
	if (dictionarySize is None):
		return

	sock.send(b'OK')

	fileDictionary = getFileDictionary (sock, dictionarySize)
	if fileDictionary is None:
		return

	pullChangedFiles (sock, fileDictionary)

	removeObsolteFiles (sock)

	sock.close()
	print('connection closed')

def passwordCheck (sock):
	clientPw = sock.recv(1024).decode()
	if password == clientPw:
		sock.send(b'OK')
	else:
		sock.send(b'CANCEL')
		sock.close()
		return

def getPath (sock):
	root = "/root/Backup"
	folder = sock.recv(1024).decode()
	root = os.path.join (root, folder)

	try:
		os.makedirs(root, exist_ok=True)
	except Exception as e:
		print("folder exists!")

	os.chdir(root)
	sock.send(b'OK')

def getDictionarySize (sock):
	try:
		#get the fileDictionary Size
		return int(sock.recv(1024).decode())
	except Exception as e:
		logf.write("Failed to get dictionary size: {0}\n".format( str(e)))
		return None;

def getFileDictionary (sock, dictionarySize):
	f = io.BytesIO(b'')
	while True:
		try:
			data = sock.recv(1024)
			f.write (data)
			if len(f.getvalue())>=dictionarySize:
				break
		except Exception as e:
			logf.write("Failed to get file dictionary: {0}\n".format( str(e)))
			return None;

	fileDictionary = ast.literal_eval(f.getvalue().decode())
	f.close()
	return fileDictionary

def pullChangedFiles (sock, fileDictionary):
	for item in fileDictionary.items():
			filename = item [0].replace ("\\","/")

			if os.path.isfile(filename):
				if os.path.getsize(filename) == item[1]:
					continue

			os.makedirs(os.path.dirname(filename),exist_ok=True)
			if item[1]==0:
				print ("Save Empty File")
				open(filename, "w+").close()
				continue

			print ("Add Or Change:", filename)
			sock.send(item[0].encode())

			totalRecv = 0
			with open(filename, 'wb') as f:
				while True:
					try:
						data = sock.recv(1024)
						f.write(data)
						totalRecv +=len(data)
						if totalRecv>=item[1]:
							break
					except Exception as e:
						logf.write("Failed get file: {0}\n{1}\n".format( filename,str(e)))
						return

	sock.send(b"#end")
	print('files received')

def removeObsolteFiles (sock):
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

		for name in subdirs:
			print (name)
			fname = os.path.join(path,name)
			if not os.listdir(fname): #to check wether the dir is empty
				print ("Delete:", fname.encode("utf-8", "surrogateescape"))
				os.removedirs(fname)

def Main():
	print ('Only works with python3! If started with python please restart with python3!')
	host = ''
	port = 5000
	global password
	with open('data.json') as data_file:
		data = json.load(data_file)
		host = data["host"]
		password = data["password"]



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
		time.sleep(1);

	s.close()


if __name__ == '__main__':
	Main()
