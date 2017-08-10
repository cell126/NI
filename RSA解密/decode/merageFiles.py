# coding=utf-8

import sys
import os.path


reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':

    rootdir = "E:\\Data\\result"

    filenameList = []

    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            print os.path.join(parent, filename)
            filenameList.append(os.path.join(parent, filename))

    filenameList.sort()

    print filenameList

    outputFile = open("e:\\decoded_encoded_output_2016-11-30_10-06-25.txt", 'w')
    for item in filenameList:
        with open(item, 'r') as inputFile:
            lines = inputFile.readlines()
            outputFile.writelines(lines)
            outputFile.flush()
    outputFile.close()
