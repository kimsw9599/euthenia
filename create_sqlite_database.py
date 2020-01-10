# -*- coding: utf-8 -*-
import sqlite3
from sqlite3 import Error
 
 
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn
 
 
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
 
 
def main():
    database = r"exchage_rate.db"
 
    tbl_currency_table = """ create table tbl_currency2(
                            id integer PRIMARY KEY,
                            currency_name text NOT NULL,
                            currency_value NUMERIC,
                            crawl_date DATE DEFAULT (datetime('now','localtime'))
                        ); """
 
    conn = create_connection(database)
 
    if conn is not None:
        create_table(conn, tbl_currency_table)
        print("Success! create table.")
    else:
        print("Error! cannot create the database connection.")
 
 
if __name__ == '__main__':
    main()