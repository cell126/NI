# coding=utf-8

import sys
import re
import os
import pandas as pd
import matplotlib.image as mpimg
import numpy as np
from sklearn.cluster import DBSCAN
from PIL import Image
import matplotlib.cbook as cbook
from sklearn import linear_model

import matplotlib.pyplot as plt

reload(sys)
sys.setdefaultencoding('utf-8')


def getPoints(inputFilename, outputFilename):
    if(not os.path.exists(inputFilename)):
        return

    with open(inputFilename, 'r') as f:
        lines = f.readlines()

    pattern = "POLYGON\(\(([\d\s,]+)\)\)"

    text = ""
    group = 0
    if (lines is not None):
        for line in lines:
            result = re.findall(pattern, line)
            for item in result:
                lineText = item.replace(',', "," + str(group) + "\n").replace(' ', ',')
                text += lineText + "," + str(group) + '\n'
                group += 1

    with open(outputFilename, 'w') as f:
        f.writelines("x,y,g" + '\n' + text)


if __name__ == '__main__':
    width = 1920
    height = 1080
    ratio = float(width) / float(1080)
    print ratio

    inputFilename = "D:\\cluster\\example\\lanemarking\\25.txt"
    outputFilename = "D:\\cluster\\example\\lanemarking\\25.csv"
    srcImageFilename = "D:\\cluster\\example\\lanemarking\\25_SemanticPolygon.png"
    tarImageFilename = "D:\\cluster\\example\\lanemarking\\_25_SemanticPolygon.png"

    getPoints(inputFilename, outputFilename)

    print("Finished!")


    #img = Image.open(srcImageFilename)
    #cropImg = img.crop((0,0,width,height))
    #cropImg.save(tarImageFilename)

    image_file = cbook.get_sample_data(tarImageFilename)
    image = plt.imread(image_file)

    df = pd.read_csv(outputFilename)
    #df['y'] = (height - df['y']) / ratio

    lr = {}
    ransac = {}
    selected = [0, 1, 4, 5]
    for i in range(df.g.max()):
        if(i not in selected):
            continue
        curdf = df[df.g == i]
        minX = curdf.x.min()
        maxX = curdf.x.max()

        model = linear_model.LinearRegression()

        X = curdf['x'].as_matrix()
        Y = curdf['y'].as_matrix()
        X.shape = (X.shape[0], 1)
        Y.shape = (Y.shape[0], 1)
        model.fit(X, Y)

        model_ransac = linear_model.RANSACRegressor(linear_model.LinearRegression())
        print i
        model_ransac.fit(X, Y)

        #line_X = np.arange(minX, maxX)
        line_X = np.arange(0, width)
        line_y = model.predict(line_X[:, np.newaxis])
        line_y_fansac = model_ransac.predict(line_X[:, np.newaxis])

        lr[i] = (line_X, line_y)
        ransac[i] = (line_X, line_y_fansac)


    #model_ransac = linear_model.RANSACRegressor(linear_model.LinearRegression())
    #model_ransac.fit(df['x'], df['y'])

    #y_pred = DBSCAN(eps=10, min_samples=3).fit_predict(df.values)

    for key in lr.keys():
        plt.plot(lr[key][0], lr[key][1], '-k', label='Linear regressor', c='b')

    for key in ransac.keys():
        plt.plot(ransac[key][0], ransac[key][1], '-b', label='RANSAC regressor', c='r')

    plt.imshow(image)
    plt.scatter(df['x'], df['y'], marker='o', c=df['g'])
    plt.show()