from flask import current_app,g
import psycopg2
from nyc_schools.backend.settings import *

conn_dev = psycopg2.connect(database = DB_NAME, user = DB_USER, host=DB_HOST,password = DB_PASSWORD, port=5432)

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(user = current_app.config['DB_USER'],password = current_app.config['DB_PASSWORD'],
            dbname = current_app.config['DATABASE'],host=current_app.config['DB_HOST'],port=5432)
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def build_from_record(Class, record):
    if not record: return None
    attr = dict(zip(Class.columns, record))
    obj = Class()
    obj.__dict__ = attr
    return obj

def build_from_records(Class, records):
   return [build_from_record(Class, record) for record in records]

def find_all(Class, cursor):
    sql_str = f"SELECT * FROM {Class.__table__}"
    cursor.execute(sql_str)
    records = cursor.fetchall()
    return [build_from_record(Class, record) for record in records]

def find(Class, id, cursor):
    sql_str = f"SELECT * FROM {Class.__table__} WHERE id = %s"
    cursor.execute(sql_str, (id,))
    record = cursor.fetchone()
    return build_from_record(Class, record)
def find_by_school_id(Class, id, cursor):
    sql_str = f"SELECT * FROM {Class.__table__} WHERE school_id = %s"
    cursor.execute(sql_str, (id,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def save(obj, conn, cursor):
    s_str = ', '.join(len(values(obj)) * ['%s'])
    obj_str = f"""INSERT INTO {obj.__table__} ({keys(obj)}) VALUES ({s_str});"""
    cursor.execute(obj_str, list(values(obj)))
    conn.commit()
    cursor.execute(f'SELECT * FROM {obj.__table__} ORDER BY id DESC LIMIT 1')
    record = cursor.fetchone()
    return build_from_record(type(obj), record)

def values(obj):
    venue_attrs = obj.__dict__
    return [venue_attrs[attr] for attr in obj.columns if attr in venue_attrs.keys()]

def keys(obj):
    school_attrs = obj.__dict__
    selected = [attr for attr in obj.columns if attr in school_attrs.keys()]
    return ', '.join(selected)

def drop_records(cursor, conn, table_name):
    cursor.execute(f"DELETE FROM {table_name};")
    conn.commit()

def drop_tables(table_names, cursor, conn):
    for table_name in table_names:
        drop_records(cursor, conn, table_name)

def drop_all_tables(conn, cursor):
    table_names = [ 'scores','attendance', 'student_population','schools']
    drop_tables(table_names, cursor, conn)

def find_by_name(Class, name, cursor):
    query = f"""SELECT * FROM {Class.__table__} WHERE name = %s """
    cursor.execute(query, (name,))
    record =  cursor.fetchone()
    obj = build_from_record(Class, record)
    return obj

def find_or_create_by_name(Class, name, conn, cursor):
    obj = find_by_name(Class, name, cursor)
    if not obj:
        new_obj = Class()
        new_obj.name = name
        obj = save(new_obj, conn, cursor)
    return obj

def find_or_build_by_name(Class, name, cursor):
    obj = Class.find_by_name(name, cursor)
    if not obj:
        obj = Class()
        obj.name = name
    return obj