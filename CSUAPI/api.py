# coding=utf-8

import sys

from flask import Flask
from flask_restful import Api

from csu.resources.dataset import DataSet, DataSetList, DataPackage

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
api = Api(app)

api.add_resource(DataSet, '/CSUAPI/v1.0/DataSet')
api.add_resource(DataSetList, '/CSUAPI/v1.0/DataSet/List')
api.add_resource(DataPackage, '/CSUAPI/v1.0/DataSet/Packages/<string:name>')


if __name__ == '__main__':
    app.run(debug=True, port=9601, host='0.0.0.0')