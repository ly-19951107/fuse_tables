# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from subprocess import Popen

app = Flask(__name__)


@app.route('/fuse-table/', methods=['POST'])
def func():
    """
    post参数的格式如下：
    {
        "task_id": "abcd",
        "table_list": ["A", "B", "C"]
        "db_type": "mysql",
        "params": {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "passwd": "123",
            "db": "mydb"
        }
    }
    :return:
    """
    args = request.json
    task_id = args['task_id']
    table_list = args['table_list']
    db_type = args['db_type']
    params = args['params']
    host = params['host']
    port = params['port']
    user = params['user']
    passwd = params['passwd']
    db = params['db']

    Popen(['python', 'run.py',
           '--task_id', task_id,
           '--table_list', table_list,
           '--db_type', db_type,
           '--host', host,
           '--port', str(port),
           '--user', user,
           '--passwd', passwd,
           '--db', db,
           ])

    return jsonify({'status': 1, 'msg': 'OK'})


if __name__ == '__main__':
    app.run('0.0.0.0')
