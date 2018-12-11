import requests
from multiprocessing import Process, RawValue, Lock
from tusclient import client
import os
from os import listdir
from os.path import isfile, join
import threading
import sys,time
import requests
import pycurl
import config
import io
# import traceback
# import urllib.parse as urlparse
from urlparse import urlparse


pass_count=0
fail_count=0
open('upload_stat.txt','w').close()
file_write=open('upload_stat.txt','a')


class Counter(object):
    def __init__(self, value=0):
        # RawValue because we don't need it to create a Lock:
        self.val = RawValue('i', value)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value

def attempts(max_attempts=3, initial_delay=0):
    for i in range(max_attempts):
		yield i

def die(msg, exit_code=0):
    print (msg)
    sys.exit(exit_code)

def get_endpt(filename):
	endpoint="http://129.114.16.189:30008/uploads/"
	filesize = os.path.getsize(filename)
	c  = requests.post(endpoint, headers={"Upload-Length": str(filesize), "Tus-Resumable": "1.0.0"})
	if c.status_code != 201:
		die("create failure. reason: %s"  % c.reason)
	print("Headers:",c.headers)
	location = c.headers["Location"]
	# location="http:"+location
	print ("Location:",location)
	p = urlparse(location, 'http')
	print(p)
	return p.geturl()
	# return location

def get_offset(location):
	h = requests.head(location,  headers={"Tus-Resumable": "1.0.0"})
	offset = int(h.headers["Upload-Offset"])
	print(h.headers)
	# print ("Offset: ", offset)
	return offset 

def upload(location, filename, offset=0, upload_speed=None):
    c = None
    content_type = "application/offset+octet-stream"
    try:
		c = pycurl.Curl()
		print("Retry")
		#c.setopt(pycurl.VERBOSE, 1)
		c.setopt(pycurl.URL, str(location))
		bout = io.BytesIO()
		hout = io.BytesIO()

		c.setopt(pycurl.HEADERFUNCTION, hout.write)
		c.setopt(pycurl.WRITEFUNCTION, bout.write)
		c.setopt(pycurl.UPLOAD, 1)
		c.setopt(pycurl.CUSTOMREQUEST, 'PATCH')

		f = open(filename, 'rb')
		if offset > 0: 
			f.seek(offset)
		c.setopt(pycurl.READFUNCTION, f.read)
		filesize = os.path.getsize(filename)
		if upload_speed:
			c.setopt(pycurl.MAX_SEND_SPEED_LARGE, upload_speed)
		c.setopt(pycurl.INFILESIZE, filesize - offset)
		c.setopt(pycurl.HTTPHEADER, ["Expect:", "Content-Type: %s" % content_type, "Upload-Offset: %d" % offset, "Tus-Resumable: 1.0.0"])
		c.perform()

		response_code = c.getinfo(pycurl.RESPONSE_CODE)
		response_data = bout.getvalue()
		response_hdr = hout.getvalue()
		#print response_data
		#print response_hdr
		print ("patch->", response_code)
		return response_code == 200
    finally:    
		if c: c.close()
		


def tester(pass_counter,fail_counter,file_name):
	url="http://129.114.16.189:30008/uploads"
	my_client = client.TusClient(url)
	fs = open(file_name)
	print("Test started")
	start_time=time.time()
	filesize = os.path.getsize(file_name)
	if not os.path.isfile(file_name):
		print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
		with open('upload_stat.txt', 'a') as the_file:
			the_file.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Failed"+", Time:"+str(sys.maxint))
		# file_write.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Failed"+"Time:"+str(sys.maxint))
		die("invalid file %s" % filename)
	filesize = os.path.getsize(file_name)
	location = get_endpt(file_name)
	for i in attempts(3):
		try:
			offset = get_offset(location)
			upload(location, file_name, offset=offset)
			offset = get_offset(location)
			if offset == filesize:
				status = "upload success"
				# print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
				with open('upload_stat.txt', 'a') as the_file:
					the_file.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Success"+", Time:"+str(time.time()-start_time))
				# file_write.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Success"+"Time:"+str(time.time()-start_time))
				break
		except Exception as e:
			print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
			


if __name__ == '__main__':
	pass_count=fail_count=0
	nos_parallel_request=int(sys.argv[1])
	# nos_process=int(sys.argv[2])
	folder_path=sys.argv[2]
	# file_list=onlyfiles = [os.path.join(folder_path,f) for f in listdir(folder_path) if isfile(join(folder_path, f))]
	file_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(sys.argv[2]) for f in filenames]
	print(file_list)
	print(len(file_list))
	url="http://129.114.16.189:30008/uploads"
	my_client = client.TusClient(url)
	my_client.set_headers({"Access-Control-Allow-Origin":'*'})
	fs = open(file_list[0])
	# print("Test started")
	start_time=time.time()
	file_counter=0
	while file_counter<len(file_list):
		procs=[]
		for i in range(nos_parallel_request):
			if(file_counter<len(file_list)):
				pass_counter=Counter(0)
				fail_counter=Counter(0)
				procs = [Process(target=tester, args=(pass_counter,fail_counter,file_list[file_counter]))]
				file_counter+=1
		for p in procs: p.start()
		for p in procs: p.join()
	file_write.close()
	
		
		
	# nos_times=int(nos_parallel_request/nos_process)
	# for file_name in file_list:
	# 	for i in range(nos_times):
	# 		pass_counter=Counter(0)
	# 		fail_counter=Counter(0)
	# 		nos_parallel_request=int(sys.argv[1])
	# 		procs = [Process(target=tester, args=(pass_counter,fail_counter,file_name)) for i in range(nos_process)]
	# 		for p in procs: p.start()
	# 		for p in procs: p.join()
	# 		print(nos_process,pass_counter.value(),fail_counter.value())
	# 		pass_count+=pass_counter.value()
	# 		fail_count+=fail_counter.value()
	# file_write.close()




