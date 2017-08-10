# coding=utf-8

import sys
import os.path

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
import time

reload(sys)
sys.setdefaultencoding('utf-8')

def decode(path, file, keyfilename):
    filename = os.path.join(path, file)

    random_generator = Random.new().read

    with open(keyfilename) as f:
        key = f.read()

    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)

    print "Decoding " + filename + "  use " + keyfilename

    encodedFile = open(filename, 'r')
  
    decodedFile = open("E:\\Data\\output\\decoded_" + file, 'w')

    startTime = time.time()
    beginTime = startTime
    lines = encodedFile.readlines()
    linesNumber = len(lines)
    n = 0
    for line in lines:
        text = cipher.decrypt(base64.b64decode(line), random_generator)
        n += 1
        if (n % 100 == 0):
            endTime = time.time()
            vol = 100.0 / (endTime - startTime)
            print('Line : %d / %d (%.2f l/s    %.1f ms/l    est: %d m %d s)' % (
            n, linesNumber, vol, 1 / vol * 1000, (linesNumber - n) / vol / 60, ((linesNumber - n) / vol) % 60))
            startTime = endTime
        if (text is not None and isinstance(text, str)):
            decodedFile.write(text + '\n')
    endTime = time.time()
    decodedFile.close()
    encodedFile.close()
    print(endTime - beginTime)
    print("Finish!")



if __name__ == '__main__':

    if(len(sys.argv) == 4):
        decode(sys.argv[1], sys.argv[2], sys.argv[3])

    '''
    rootdir = "E:\\Data\\BMW"

    filenameList = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            print os.path.join(parent, filename)
            filenameList.append(os.path.join(parent, filename))

    
    random_generator = Random.new().read
    
    with open('test_4096_v1.key') as f:
        key = f.read()
    
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)

    for filename in filenameList:
        print "Decoding " + filename
        encodedFile = open(filename, 'r')
        decodedFile = open(filename + ".decoded", 'w')
    
        startTime = time.time()
        beginTime = startTime
        lines = encodedFile.readlines()
        linesNumber = len(lines)
        n = 0
        for line in lines:
    
            text = cipher.decrypt(base64.b64decode(line), random_generator)
            n += 1
            if (n % 100 == 0):
                endTime = time.time()
                vol = 100.0 / (endTime - startTime)
                print('Line : %d / %d (%.2f l/s    %.1f ms/l    est: %d m %d s)' % (n, linesNumber, vol, 1 / vol * 1000, (linesNumber-n)/vol/60, ((linesNumber-n)/vol) % 60))
                startTime = endTime
            if(text is not None and isinstance(text, str)):
                decodedFile.write(text + '\n')
        endTime = time.time()
        decodedFile.close()
        encodedFile.close()
    
    print(endTime - beginTime)
    print("Finish!")
    '''
