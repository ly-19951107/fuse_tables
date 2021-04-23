import cx_Oracle
import pymysql
from util_log import gen_logger
from configparser import ConfigParser
from os.path import split, abspath

logger = gen_logger('./main_log')
current_path = split(abspath(__file__))[0]
cfg = ConfigParser()
with open(current_path + '/application.cfg', encoding='utf-8') as f:
    cfg.read_file(f)


def main(task_id, **kwargs):
    if not kwargs:
        flag = 0
        logger.info('离线条件下获取参数')
        sql_cfg = cfg.get('task_sql', 'sql_cfg')
        table = cfg.get('table_list', 'table_list')
        table_list = eval(table)
        sql_cfg = {**eval(sql_cfg)}
        db_type = sql_cfg['db_type']
        host = sql_cfg['host']
        port = sql_cfg['port']
        user = sql_cfg['user']
        passwd = sql_cfg['password']
        db = sql_cfg['db']
    else:
        flag = 1
        logger.info('非离线条件下获取参数')
        table_list = kwargs['table_list']
        db_type = kwargs['db_type']
        host = kwargs['host']
        port = kwargs['port']
        user = kwargs['user']
        passwd = kwargs['passwd']
        db = kwargs['db']
    dic_list = []
    key_list = []
    for num in range(len(table_list)):
        dic_list.append(f'dic_{num}')
        key_list.append(f'key_{num}')

    # 将每张表的字段名以及注释以键值对的方式分别存入字典中
    logger.info('连接数据库')
    conn = connect(db_type, host, port, user, passwd, db, logger)
    with conn.cursor() as cr:
        for i in range(len(table_list)):
            if db_type.upper() == 'ORACLE':
                cr.execute(f"select COLUMN_NAME, COMMENTS from user_col_comments where Table_Name='{table_list[i]}'")
            if db_type.upper() == 'MYSQL':
                cr.execute(f"select COLUMN_NAME, COMMENTS from information_schema.COLUMNS "
                           f"where Table_Name='{table_list[i]}'")
            sql_res = cr.fetchall()
            dic_list[i] = {}
            for j in sql_res:
                dic_list[i][j[0]] = j[1]

    logger.info('对比表中字段名是否相同')
    dic_keys = {}
    for t in range(len(dic_list)):
        for t1 in range(t + 1, len(dic_list)):
            for k in dic_list[t].keys():
                for k1 in dic_list[t1].keys():
                    if k == k1:
                        if k not in dic_keys:
                            dic_keys[k] = [table_list[t], table_list[t1]]
                        else:
                            if table_list[t] not in dic_keys[k]:
                                dic_keys[k].append(table_list[t])
                            if table_list[t1] not in dic_keys[k]:
                                dic_keys[k].append(table_list[t1])

    logger.info('对于字段名称不相同的，求字段注释间的相似度')
    for n in range(len(key_list)):
        key_list[n] = list(set(dic_list[n].keys()) - set(dic_keys.keys()))
        if key_list[n] is None:
            continue
        else:
            max_sim = 0.85
            for e in key_list[n]:
                for n1 in range(n + 1, len(key_list)):
                    for k2 in dic_list[n1].keys():
                        if sims(dic_list[n][e], dic_list[n1][k2]) > max_sim:
                            if e not in dic_keys:
                                dic_keys[e] = [table_list[n], table_list[n1]]
                            else:
                                if table_list[n] not in dic_keys[e]:
                                    dic_keys[e].append(table_list[n])
                                if table_list[n1] not in dic_keys[e]:
                                    dic_keys[e].append(table_list[n1])
                else:
                    dic_keys[e] = [table_list[n]]

    logger.info('将结果存入表格中')
    dic_res = {'map_num': [], 'name': [], 'comment': [], 'data_type': [], 'source_table': []}
    for x in dic_keys.keys():
        dic_res['map_num'].append(len(dic_keys[x]))
        dic_res['name'].append(x)
        cr = conn.cursor()
        if db_type.upper() == 'ORACLE':
            cr.execute(f"select b.COMMENTS, a.data_type from user_tab_columns a, user_col_comments b "
                       f"where a.table_name='{dic_keys[x][0]}' and b.table_name='{dic_keys[x][0]}' and "
                       f"a.column_name='{x}' and b.column_name='{x}'")
        if db_type.upper() == 'MYSQL':
            cr.execute(f"select COLUMN_COMMENT, DATA_TYPE from information_schema.COLUMNS "
                       f"where table_name = '{dic_keys[x][0]}' and column_name='{x}'")
        info = cr.fetchall()[0]
        dic_res['comment'].append(info[0])
        dic_res['data_type'].append(info[1])
        dic_res['source_table'].append(dic_keys[x])

    save_to_sql(dic_res, flag, conn)


def connect(db_type, host, port, user, passwd, db, logger):
    if db_type.upper() == 'MYSQL':
        conn = pymysql.connect(host=host, port=port, user=user, password=passwd, db=db)
    elif db_type.upper() == 'ORACLE':
        dsn = cx_Oracle.makedsn(host, port, service_name=db)
        conn = cx_Oracle.connect(user, passwd, dsn, encoding='UTF-8')
    else:
        logger.error('不支持的数据库类型')
        raise
    return conn


def save_to_sql(dic_res, flag, conn):
    # 将字典存入数据库
    if flag == 0:
        sql_cfg = cfg.get('res_sql', 'sql_cfg')
        sql_cfg = {**eval(sql_cfg)}
        db_type = sql_cfg['db_type']
        host = sql_cfg['host']
        port = sql_cfg['port']
        user = sql_cfg['user']
        passwd = sql_cfg['password']
        db = sql_cfg['db']
        conn = connect(db_type, host, port, user, passwd, db, logger=None)
    else:
        conn = conn
    cur = conn.cursor()
    # table = "res_table"
    for i in range(len(dic_res['map_num'])):
        m = dic_res['map_num'][i]
        n = dic_res['name'][i]
        c = dic_res['comment'][i]
        d = str(dic_res['data_type'][i])
        s_t = ','.join(dic_res['source_table'][i])
        sql = f"insert into res_table values ('{m}', '{n}', '{c}', '{d}', '{s_t}')"
        cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def sims(string1, string2):
    if not isinstance(string1, str):
        return 0
    if not isinstance(string2, str):
        return 0
    sim = lvst_dis(string1, string2)
    return sim


def lvst_dis(string1, string2) -> float:
    """Return the edit distance of two strings.

    Args:
        string1(str): 1st string
        string2(str): 2nd string

    Returns:
        Similarity value
    """
    import Levenshtein as Lvst
    dis = Lvst.distance(string1, string2)
    return 1 - dis / max(len(string1), len(string2))
