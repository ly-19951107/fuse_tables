# -*- coding: utf-8 -*-
import argparse
from main_app import main


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task_id', type=str, help="识别任务的唯一标识")
    parser.add_argument('--table_list', type=list, help="需要融合的数据表列表")
    parser.add_argument('--db_type', type=str, help="数据库类型")
    parser.add_argument('--host', type=str, help='数据库的ip地址')
    parser.add_argument('--port', type=int, help="数据库的端口号")
    parser.add_argument('--user', type=str, help='用户名')
    parser.add_argument('--passwd', type=str, help='密码')
    parser.add_argument('--db', type=str, help='数据库名称')  # 数据库名称，如果是oracle数据库，则为实例名

    args = parser.parse_args()

    task_id = args.task_id
    table_list = args.table_list
    db_type = args.db_type
    host = args.host
    port = args.port
    user = args.user
    passwd = args.passwd
    db = args.db

    if not task_id:  # 未传入任务的id，这说明是在离线调用模型
        task_id = 'test_task'
        main(task_id)
    else:
        main(task_id, table_list=table_list, db_type=db_type, host=host, port=port, user=user, passwd=passwd, db=db)
