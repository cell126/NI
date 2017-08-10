# coding=utf-8

import sys
import os.path
import pandas as pd
import datetime as dt
import time
import re

reload(sys)
sys.setdefaultencoding('utf-8')


def processDatetime(timestr):
    datetime = []
    split = [4,2,2,2,2,2,3]
    at = 0
    timestr = list(timestr)
    for i in range(len(split)):
        a = timestr[at:at+split[i]]
        datetime.append(int("".join(timestr[at:at+split[i]])))
        at += split[i]
    datatime = dt.datetime(datetime[0], datetime[1], datetime[2], datetime[3], datetime[4], datetime[5], datetime[6]*1000)
    return time.mktime(datatime.timetuple())


def processFile(filename, parent):
    if(not os.path.exists(filename)):
        return None
    df = None
    pattern = "(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})(((0[13578]|1[02])(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)(0[1-9]|[12][0-9]|30))|(02(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)"
    with open(filename) as fs:
        lines = []
        columns = ["timestamp", "longitude", "latitude", "filename"]
        data = fs.readlines()
        for itemLine in data:
            items = itemLine.strip().split(',')
            if(len(items[0]) == 9):
                paths = parent.split(os.path.sep)
                for item in paths:
                    result = re.match(pattern, item)
                    if(result is not None):
                        print result.group() + items[0]
                        items[0] = processDatetime(result.group() + items[0]) * 1000
            if(len(items) == 4):
                lines.append(items)
            else:
                l = items[0:3]
                l.append(items[-1])
                lines.append(l)
        df = pd.DataFrame(data=lines, columns=columns)
        df['datetime'] = df['timestamp'].apply(lambda t: dt.datetime.fromtimestamp(float(t)/1000.0))
    return df

if __name__ == '__main__':
    data = {}
    dfs = []
    rootdir = "e:\\test"
    #rootdir = "/data01/data"
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            os.path.join(parent, filename)
            if (str.lower(filename) == "gps.txt"):
                fullname = os.path.join(parent, filename)
                df = processFile(fullname, parent)
                if(df is not None):
                    data[fullname] = df
                dfs.append(df)
    gps = pd.concat(dfs)
    gps.to_csv("gps.csv")