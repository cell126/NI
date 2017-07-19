# coding=utf-8

import sys
import os

try:
  import xml.etree.cElementTree as et
except ImportError:
  import xml.etree.ElementTree as et

import numpy as np
import pandas as pd
import datetime as dt
import math

reload(sys)
sys.setdefaultencoding('utf-8')



class Translator:
    matrix = None

    def setPara(self,deltX=0.0, deltY=0.0, deltZ=0.0, thetaX=0.0, thetaY=0.0, thetaZ=0.0, isreverse = False):
        translationMat = np.identity(4)
        translationMat[0, 3] = deltX;
        translationMat[1, 3] = deltY;
        translationMat[2, 3] = deltZ;

        rotXMat = np.identity(4)
        rotXMat[1, 1] =  math.cos(thetaX)
        rotXMat[1, 2] = -math.sin(thetaX)
        rotXMat[2, 1] =  math.sin(thetaX)
        rotXMat[2, 2] =  math.cos(thetaX)

        rotYMat = np.identity(4)
        rotYMat[0, 0] =  math.cos(thetaY)
        rotYMat[0, 2] =  math.sin(thetaY)
        rotYMat[2, 0] = -math.sin(thetaY)
        rotYMat[2, 2] =  math.cos(thetaY)

        rotZMat = np.identity(4)
        rotZMat[0, 0] =  math.cos(thetaZ)
        rotZMat[0, 1] = -math.sin(thetaZ)
        rotZMat[1, 0] =  math.sin(thetaZ)
        rotZMat[1, 1] =  math.cos(thetaZ)

        reverseMat = np.identity(4)
        if ( isreverse ):
            reverseMat[2, 2] = -1

        self.matrix = np.linalg.multi_dot([translationMat, rotXMat, rotYMat, rotZMat, reverseMat])



    def translate(self, coordinate):
        if (self.matrix is not None and coordinate is not None and (len(coordinate) == 3 or len(coordinate == 4))):
            length = len(coordinate)
            if (len(coordinate) == 3 ):
                if (coordinate.shape[0] == 3):
                    coordinate = np.insert(coordinate, len(coordinate), axis=0, values=[1.0])
                else:
                    coordinate = np.insert(coordinate, len(coordinate), axis=1, values=[1.0])
            coordinate = coordinate.reshape(4, 1)
            coordinate[3] = 1.0 if coordinate[3] == 0 else coordinate[3]
            result = self.matrix.dot(coordinate)
            result = result / result[3]
            if(length == 3):
                return result[:3].reshape(1, 3)[0]
            else:
                return result.reshape(1, 4)[0]
        return None



class DataFile:
    fileName = None
    data = {}
    dataFrames = {}
    lanemarking = {}

    def __init__(self, fileName):
        self.fileName = fileName


    def __readFile(self):
        if (os.path.exists(self.fileName)):
            file = open(self.fileName, 'r')
            try:
                data = file.read()
            finally:
                file.close()
        return data


    def __processFile(self):
        data = '<?xml version="1.0" encoding="ISO-8859-1"?><Data>' + self.__readFile() + '</Data>'
        tree = et.fromstring(data)
        types = ['vehicleStatus', 'GPS', 'Lanemarking', 'Odometry', 'Location']

        for type in types:
            self.data[type] = self.__iterate(type, tree)
            if type == 'Lanemarking':
                self.dataFrames[type] = self.__processLanemarking(self.data[type])
            else:
                self.dataFrames[type] = self.__processDataFrame(self.data[type])

            if ( self.dataFrames[type] is not None and 'second' in (self.dataFrames[type]).columns ):
                self.dataFrames[type]['timestamp'] = self.dataFrames[type]['second'] + '.' + \
                                                     self.dataFrames[type]['nanosecond']
                self.dataFrames[type]['timestamp'] = self.dataFrames[type]['timestamp'].astype('float64')
                self.dataFrames[type]['datetime'] = self.dataFrames[type]['timestamp'].\
                    apply(lambda t: dt.datetime.fromtimestamp(t))
                self.dataFrames[type] = self.dataFrames[type].drop('timestamp', 1)


    def __processLanemarking(self, data):
        headers = ""
        values = ""
        seq = ""

        lines = data.strip().split('\n')

        for line in lines:
            items = line.strip().split(",")

            if( (items is not None) and (len(items) == 3) and (items[2].strip().split(":")[0] == 'sequence') ):
                if(len(values) > 0):
                    df = self.__processDataFrame(values)
                    self.lanemarking[seq] = df
                    values = ""
                seq = (items[2].strip().split(":")[1]).strip()
                headers += line + "\n"
            else:
                if(len(line) > 0):
                    values += line + "\n"
        if(len(values) > 0):
            df = self.__processDataFrame(values)
            self.lanemarking[seq] = df

        if(len(headers) > 0):
            df = self.__processDataFrame(headers)
            return df


    def __processDataFrame(self, data):
        lines = []
        keys = []

        for itemLine in data.strip().split('\n'):
            line = []
            for item in itemLine.strip().split(','):
                v = item.split(':')
                if (len(v) == 2):
                    key = v[0].strip()
                    if key not in keys:
                        keys.append(key)
                    value = v[1].strip()
                    line.append(value)
            lines.append(line)
        df = pd.DataFrame(data=lines, columns=keys)
        return df


    def __iterate(self, typeName, tree):
        result = ""
        for item in tree.findall(typeName):
            result += item.text + '\n'
        return result


    def getData(self, type='GPS', seq=""):
        if (len(self.dataFrames) == 0):
            self.__processFile()

        if (type == 'Lanemarking' and len(seq) > 0):
            return self.lanemarking[seq]

        return self.dataFrames[type]



class PointCloud:
    data = pd.DataFrame()
    tran = Translator()
    str = ""

    def __init__(self):
        return


    def appendData(self, dataframe, deltX=0.0, deltY=0.0, deltZ=0.0, thetaX=0.0, thetaY=0.0, thetaZ=0.0, isreverse = False):
        if ( dataframe is not None):
            result = self.__translateCoord(dataframe, deltX, deltY, deltZ, thetaX, thetaY, thetaZ, isreverse)
            self.data = self.data.append(result)

    def __translateCoord(self, dataframe, deltX, deltY, deltZ, thetaX, thetaY, thetaZ, isreverse):
        self.tran.setPara(deltX, deltY, deltZ, thetaX, thetaY, thetaZ, isreverse)
        result = []
        for i in range(len(dataframe)):
            coord = np.array([dataframe.iat[i, 0], dataframe.iat[i, 1], dataframe.iat[i, 2]])
            coord = coord.astype('float64')
            record = self.tran.translate(coord).astype('float')
            self.str += str.format("%.10f" % record[0]) + ' ' + str.format("%.10f" % record[1]) + ' ' + \
                        str.format("%.10f" % record[2]) + "\n"
            result.append(record)
        return pd.DataFrame(result)


    def __getHeader(self, width, points):
        header = "# .PCD v.5 - Point Cloud Data file format \nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\n" \
                 "WIDTH %d\nHEIGHT 1\nPOINTS %d\nDATA ascii\n" % (width, points)
        return header


    def to_pcd(self, filename):
        if (self.data is None):
            return
        header = self.__getHeader(self.data.shape[0], self.data.shape[0])
        datastring = self.data.to_string(header=False, index=False)

        file_object = open(filename, 'w')
        try:
            file_object.write(header + self.str)
        finally:
            file_object.close()
            print "%d points" % self.data.shape[0]


    def to_csv(self, filename):
        if (self.data is not None):
            self.data.to_csv(filename, index=False)






if __name__ == '__main__':
    dataFile = DataFile("d:\\decoded_output_170704.txt")
    #print dataFile.getData()
    print "============================================="
    types = ['vehicleStatus', 'GPS', 'Lanemarking', 'Odometry', 'Location']
    value = 1
    dfs = []
    for item in types:
        df = dataFile.getData(item)
        df = df[['datetime', 'second', 'nanosecond']]
        df = df.set_index("datetime")
        df['value'] = value
        df['type'] = item
        value += 1
        dfs.append(df)

    all = pd.concat(dfs)
    # all.plot()

    x = 641051.151525842
    y = 3449604.90289289
    pc = PointCloud()
    pc.appendData(dataFile.getData("Lanemarking", "599")[['x', 'y', 'z']], x, y, 0.0,  0.0, 0.0, -70.0/180.0*math.pi, True)
    pc.to_pcd("d:\\t.pcd")
    pc.to_csv("d:\\t.csv")

    tran = Translator()
    tran.setPara(0.0, 0.0, 0.0, 90./180.0*math.pi, 0.0, 0.0, True)


    coor = np.array([1, 1, 1, 1])
    print tran.translate(coor)
