# coding=utf-8

import sys
import os.path
from PIL import Image
import pandas as pd

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    #rootdir = "e:\\test"
    rootdir = "/data01/data"

    filenumber = {}
    fileinfo = {}
    files = [[]]
    n = 0
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            files.append([parent, filename])

    for item in files:
        if(len(item) != 2):
            continue

        parent = item[0]
        filename = item[1]
        result = os.path.splitext(filename)
        if (result is not None and len(result) == 2 and str.lower(result[1]) == '.jpg'):
            if(filenumber.has_key(parent)):
                filenumber[parent] += 1
            else:
                filenumber[parent] = 0
                with Image.open(os.path.join(parent, filename)) as img:
                    print img.size
                    fileinfo[parent] = img.size

    print filenumber
    print fileinfo

    data = []
    for dirname, number in filenumber.items():
        print (dirname, number)
        data.append([dirname, number, fileinfo[dirname][0], fileinfo[dirname][1]])

    df = pd.DataFrame(data, columns=["path", "number", "x", "y"])
    df.to_csv("imageInfo.csv")
