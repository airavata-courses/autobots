import requests
from multiprocessing import Process, RawValue, Lock
import threading
import sys,time
pass_count=0
fail_count=0
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
def tester(pass_counter,fail_counter):
	url="http://129.114.16.189:30008/uploads"
	# print("Test started")
	start_time=time.time()
	
	try:
		response=requests.options(url)
		if(time.time()-start_time<=1):
		# print(response.status_code)
			if(response.status_code==204):
				# pass_count=pass_count+1
				pass_counter.increment()
			else:
				# fail_count=fail_count+1
				fail_counter.increment()
			# print ("fail")
		else:
			fail_counter.increment()
	except Exception as E:
		fail_counter.increment()
	
	
if __name__ == '__main__':
    
	pass_count=fail_count=0
	nos_parallel_request=int(sys.argv[1])
	nos_process=int(sys.argv[2])
	nos_times=int(nos_parallel_request/nos_process)
	for i in range(nos_times):
		pass_counter=Counter(0)
		fail_counter=Counter(0)
		nos_parallel_request=int(sys.argv[1])
		procs = [Process(target=tester, args=(pass_counter,fail_counter)) for i in range(nos_process)]
		for p in procs: p.start()
		for p in procs: p.join()
		print(nos_process,pass_counter.value(),fail_counter.value())
		pass_count+=pass_counter.value()
		fail_count+=fail_counter.value()





