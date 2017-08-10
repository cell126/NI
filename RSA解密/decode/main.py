import subprocess
import sys
import os
import time

rootdir = "E:\\Data\\0"

filenameList = []
processes = []
beginTime = time.time()

for parent, dirnames, filenames in os.walk(rootdir):
    for filename in filenames:
        print os.path.join(parent, filename)
        proc = subprocess.Popen(['python', 'Decoder.py', parent, filename, "e:\\data\\test_4096_v1.key"], creationflags =subprocess.CREATE_NEW_CONSOLE)
        filenameList.append(os.path.join(parent, filename))
        processes.append(proc)

for proc in processes:
	proc.wait()

print(endTime - beginTime)
print("Finish!")