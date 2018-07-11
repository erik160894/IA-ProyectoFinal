#!/usr/bin/env python3

import pymysql
import argparse
import csv


select_query = """
select id, tag from `{table}`
where tag is not null
"""


def save_records(cursor, f_csv, sql):
    cursor.execute(sql)
    f_csv.writerow(['id', 'tag'])
    for row in cursor.fetchall():
        f_csv.writerow([row['id'], row['tag']])


def run(args):
    connection = pymysql.connect(host=args.db_host, user=args.db_user, password=args.db_pass,
                                 db=args.db_name, cursorclass=pymysql.cursors.DictCursor)

    sql = select_query.format(table=args.db_table)
    if not args.multi_tag:
        sql += " and tag not like '%,%'"

    with connection.cursor() as cursor:
        with open(args.out_file, 'w') as f:
            f_csv = csv.writer(f)
            save_records(cursor, f_csv, sql)

    connection.commit()
    connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_host', type=str, default='127.0.0.1', help='Host of the mysql')
    parser.add_argument('--db_user', type=str, default='root', help='User of mysql')
    parser.add_argument('--db_name', type=str, default='ia', help='Db name')
    parser.add_argument('--db_pass', type=str, default='hola123', help='Password of the user')
    parser.add_argument('--db_table', type=str, default='dataset', help='Table od the db where data will be stored')
    parser.add_argument('--out_file', '-o', type=str, default='tags.csv', help='Output file name')
    parser.add_argument('--multi_tag', '-mt', action='store_true', default=False)

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
