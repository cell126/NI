# coding=utf-8

import sys

from flask import Flask
from flask_restful import Api

from csu.resources.dataset import DataSet, DataSetList, DataPackage

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
api = Api(app)

api.add_resource(DataSet, '/csuapi/v1.0/dataset')
api.add_resource(DataSetList, '/csuapi/v1.0/dataset/list')
api.add_resource(DataPackage, '/csuapi/v1.0/dataset/packages/<string:name>')


if __name__ == '__main__':
    app.run(debug=True, port=9601, host='0.0.0.0')