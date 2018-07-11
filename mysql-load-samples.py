#!/usr/bin/env python3

import pymysql
import argparse
import os
import re
import datetime


create_table_query = """
create table `{table}` (
  id         varchar(32) primary key,
  anio       mediumint not null ,
  mes        tinyint not null ,
  dia        tinyint not null ,
  dia_semana tinyint not null ,
  hora       tinyint not null ,
  minuto     tinyint not null ,
  segundo    tinyint not null ,
  tag        varchar(100),
  tagger     varchar(50),
  index `{table}_index`(tag)
)
"""

insert_record_query = """
insert into `{table}`(id, anio, mes, dia, dia_semana, hora, minuto, segundo)
values(%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update id = %s
"""


def check_table(conn, db_table, replace_data):
    with conn.cursor() as cursor:
        query = "show tables like '{table}'".format(table=db_table)

        cursor.execute(query)
        resp = cursor.fetchall()

        if len(resp) > 0:
            if replace_data:
                cursor.execute('drop table `{table}`'.format(table=db_table))
                cursor.execute(create_table_query.format(table=db_table))
            else:
                print('Table already exists in db. If you want to replace data, --replace_data flag should be used.')

    return True


def run(args):
    if not os.path.exists(args.source):
        raise Exception('Source folder not found')
    if not os.path.isdir(args.source):
        raise Exception('Source id not a folder')

    connection = pymysql.connect(host=args.db_host, user=args.db_user, password=args.db_pass,
                                 db=args.db_name, cursorclass=pymysql.cursors.DictCursor)

    if not check_table(connection, args.db_table, args.replace_data):
        return

    sql = insert_record_query.format(table=args.db_table)

    with connection.cursor() as cursor:
        samples = os.listdir(args.source)
        print(len(samples), 'samples to upload.')

        for i, name in enumerate(samples):
            print('\rUploading', str(int((i+1)*100.0/len(samples))) + '%', 'percent...', end='')
            p = name.split('.')
            if p[-1] != 'mp3':
                continue
            _, timestamp = re.search('([a-zA-Z_]*)([0-9]*)', name).group(1, 2)
            date = datetime.datetime.fromtimestamp(int(timestamp))
            date = date - datetime.timedelta(minutes=int(args.timezone*60))
            cursor.execute(sql, (p[0], date.year, date.month, date.day,
                                 date.weekday(), date.hour, date.minute, date.second, p[0]))
        print('')

    connection.commit()
    connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_host', type=str, default='127.0.0.1', help='Host of the mysql')
    parser.add_argument('--db_user', type=str, default='root', help='User of mysql')
    parser.add_argument('--db_name', type=str, default='ia', help='Db name')
    parser.add_argument('--db_pass', type=str, default='hola123', help='Password of the user')
    parser.add_argument('--db_table', type=str, default='dataset', help='Table od the db where data will be stored')
    parser.add_argument('--timezone', type=float, default=-5, help='Timezone, default is -5 (Lima)')
    parser.add_argument('--replace_data', '-rd', action='store_true',
                        default=False, help='Replace table if exists')

    parser.add_argument('source', type=str)

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
