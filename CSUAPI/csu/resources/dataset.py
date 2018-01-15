# coding=utf-8

import sys

from flask import Flask
from flask_restful import Resource, reqparse
from flask import abort

from ..common.dataset_dao import DataSetDAO
import json

reload(sys)
sys.setdefaultencoding('utf-8')


parser = reqparse.RequestParser()
parser.add_argument('topic', type=str, help='Need a topic.', required=True, location='args')



class DataSet(Resource):
    def get(self):
        return '"{ "code":0, "status": "success" }"'



class DataSetList(Resource):
    def get(self):
        dao = DataSetDAO()
        dirs, dirInfo = dao.getDirs()
        dirs = json.dumps({"code": 0, "status": "success", "dataset": dirs})
        return json.loads(dirs)



class DataPackage(Resource):
    def get(self, name):
        dao = DataSetDAO()
        dirs, dirInfo = dao.getDirs()
        if(dao.exist(name)):
            ret = {}
            ret["code"] = 0
            ret["status"] = "success"
            ret["info"] = dirInfo[name]
        else:
            ret = '"{ "code":-1, "status": "failed", "name": %s }"' % name
        return ret


    def put(self, name):
        dao = DataSetDAO()
        args = parser.parse_args()
        ret = '{ "code":-1, "status": "failed", "name": %s, "topic": "%s" }' % (name, args['topic'])
        if (dao.exist(name) and len(args['topic']) > 0):
            try:
                if(dao.copyDir(name, args['topic'])):
                    ret = '{ "code":0, "status": "success", "name": "%s", "topic": "%s" }' % (name, args['topic'])
                    return json.loads(ret)
            except IOError, e:
                ret = '{ "code":-1, "status": "failed", "reason": "%s"}' % e.message
                return json.loads(ret)
        return json.loads(ret)
