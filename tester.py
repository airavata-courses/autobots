import requests
# from multiprocessng import Process, RawValue, Lock
from multiprocessing import Pool
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
from paramiko import SSHClient
from scp import SCPClient
# import traceback
# import urllib.parse as urlparse
from urlparse import urlparse


pass_count=0
fail_count=0
open('upload_stat.txt','w').close()
open('scp_upload_stat.txt','w').close()
file_write=open('upload_stat.txt','a')
file_write_2=open('scp_upload_stat.txt','a')

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
	# print("Headers:",c.headers)
	location = c.headers["Location"]
	# location="http:"+location
	# print ("Location:",location)
	p = urlparse(location, 'http')
	# print(p)
	return p.geturl()
	# return location

def get_offset(location):
	h = requests.head(location,  headers={"Tus-Resumable": "1.0.0"})
	offset = int(h.headers["Upload-Offset"])
	# print(h.headers)
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
		# if upload_speed:
		# 	c.setopt(pycurl.MAX_SEND_SPEED_LARGE, upload_speed)

		c.setopt(pycurl.INFILESIZE, filesize - offset)
		c.setopt(pycurl.HTTPHEADER, ["Expect:", "Content-Type: %s" % content_type, "Upload-Offset: %d" % offset, "Tus-Resumable: 1.0.0"])
		c.perform()

		response_code = c.getinfo(pycurl.RESPONSE_CODE)
		response_data = bout.getvalue()
		response_hdr = hout.getvalue()
		#print response_data
		#print response_hdr
		# print ("patch->", response_code)
		return response_code == 200
    finally:    
		if c: c.close()
		


def tester(file_name):
	print("for file:{value}").format(value=file_name)
	url="http://129.114.16.189:30008/uploads"
	my_client = client.TusClient(url)
	fs = open(file_name)
	# print("Test started")
	start_time=time.time()
	filesize = os.path.getsize(file_name)
	if not os.path.isfile(file_name):
		# print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
		with open('upload_stat.txt', 'a') as the_file:
			the_file.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Failed"+", Time:"+str(sys.maxint))
		# file_write.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Failed"+"Time:"+str(sys.maxint))
		# die("invalid file %s" % file_name)
		return False
	filesize = os.path.getsize(file_name)
	location = get_endpt(file_name)
	for i in attempts(3):
		try:
			offset = get_offset(location)
			upload(location, file_name, offset=offset,upload_speed=3000)
			offset = get_offset(location)
			if offset == filesize:
				status = "upload success"
				# print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
				with open('upload_stat.txt', 'a') as the_file:
					the_file.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Success"+", Time:"+str(time.time()-start_time))
				# file_write.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Success"+"Time:"+str(time.time()-start_time))
				return True
		except Exception as e:
			# print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
			print(str(e))
			with open('upload_stat.txt', 'a') as the_file:
				the_file.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Failed"+", Time:"+str(sys.maxint))
		
			return False
			
def scp_tester(file_name):
	ssh = SSHClient()
	ssh.load_system_host_keys()
	ssh.connect(hostname='129.114.16.189',username='navmarri')
	print("Test started")
	start_time=time.time()
	filesize = os.path.getsize(file_name)
	if not os.path.isfile(file_name):
		print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
		with open('scp_upload_stat.txt', 'a') as the_file:
			the_file.write("\nFile_name:"+file_name+",Size:"+str(filesize)+",Status:Failed"+", Time:"+str(sys.maxint))
	else:
		try:
			with SCPClient(ssh.get_transport()) as scp:
				scp.put(file_name, '/home/navmarri/FileUploads/'+file_name.split('/')[-1])
			
			with open('scp_upload_stat.txt', 'a') as the_file:
				the_file.write("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Success"+", Time:"+str(time.time()-start_time))
			# return True
		except Exception as e:
			print("Failure in scp")
			print(str(e))
			# print("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))
			with open('scp_upload_stat.txt', 'a') as the_file:
				the_file.write("\nFile_name:"+file_name+", Size:"+str(filesize)+", Status:Failed"+", Time:"+str(sys.maxint))

if __name__ == '__main__':
	pass_count=fail_count=0
	nos_parallel_request=int(sys.argv[1])
	# nos_process=int(sys.argv[2])
	folder_path=sys.argv[2]
	# file_list=onlyfiles = [os.path.join(folder_path,f) for f in listdir(folder_path) if isfile(join(folder_path, f))]
	file_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(sys.argv[2]) for f in filenames]
	# pool=Pool(processes=nos_parallel_request)
	# pool.map(tester,file_list)
	# pool=Pool(processes=nos_parallel_request)
	# pool.map(scp_tester,file_list)
	for each_file in file_list:
		tester(each_file)
		scp_tester(each_file)