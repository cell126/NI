# coding=utf-8

import sys

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
import time

reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':
    random_generator = Random.new().read
    
    with open('test_4096_v1.key') as f:
        key = f.read()
    
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    
    encodedFile = open('encoded_output_0719.txt', 'r')
    
    decodedFile = open('decoded_output_0719.txt', 'w')
    
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
            print('Line : %d / %d (%.2f l/s    %.1f ms/l    est: %.1f s)' % (n, linesNumber, vol, 1 / vol * 1000, (linesNumber-n) / vol))
            startTime = endTime
        #print text
        if(text is not None and isinstance(text, str)):
            decodedFile.write(text + '\n')
    endTime = time.time()
    decodedFile.close()
    encodedFile.close()
    
    print(endTime - beginTime)
    print("Finish!")
