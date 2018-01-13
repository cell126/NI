# coding=utf-8

import sys
import os.path
import shutil

reload(sys)
sys.setdefaultencoding('utf-8')


class DataSetDAO():

    srcRootDir = "e:\\src\\DataSet"
    desRootDir = "e:\\des\\DataSet"

    def getDirInfo(self, path):
        totalSize  = 0
        totalCount = 0
        if (os.path.exists(path) == False):
            return (totalSize, totalCount)

        for parent, dirnames, filenames in os.walk(path):
            for filename in filenames:
                fullpath = os.path.join(parent, filename)
                size = os.path.getsize(fullpath)
                totalSize += size
                totalCount += 1
        return (totalSize, totalCount)


    def getDirs(self):
        if (os.path.exists(self.srcRootDir)  == False):
            return [], {}

        dirs = []
        dirInfo = {}
        for parent, dirnames, filenames in os.walk(self.srcRootDir):
            for dirname in dirnames:
                if (parent != self.srcRootDir):
                    continue
                size, count = self.getDirInfo(os.path.join(parent, dirname))
                if(size != 0 and count != 0):
                    fullpath = os.path.join(parent, dirname)
                    createdTime = os.path.getctime(fullpath)
                    modifiedTime = os.path.getmtime(fullpath)
                    dirInfo[dirname] = {"name": dirname, "size": size, "count": count}
                    dirs.append({"name": dirname, "size": round(size/float(1024 * 1024), 1), "count": count, "createdTime": createdTime, "modifiedTime": modifiedTime})
        return dirs, dirInfo


    def exist(self, name):
        dirs, dirInfo = self.getDirs()
        return name in dirInfo


    def copyDir(self, srcName, desName):
        if(self.exist(srcName)):
            if (not os.path.exists(os.path.join(self.srcRootDir, srcName))):
                raise IOError("The source of %s is not existed." % srcName)

            if(not os.path.exists(os.path.join(self.desRootDir, desName))):
                shutil.copytree(os.path.join(self.srcRootDir, srcName), os.path.join(self.desRootDir, desName))
                return True
            else:
                raise IOError("The %s has been existed." % desName)
        return False