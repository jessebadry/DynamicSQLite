import sqlite3
import time
import traceback
import random
from string import ascii_letters


# the database expects all models to have an 'id' key within its data


def create_empty_model(table, *columns):
    if isinstance(columns[0], list):
        columns = columns[0]
    data = {}
    for col in columns:
        data[col] = None
    return DbModelR(table, data, use_id=False)


def quote(string):
    return '\'' + string + '\''


#  basic params for SQLite e.g (update movies SET author = Jeff, producer  = Leonard ect..)
def compile_basic_params(cols, vals):
    cols = ''.join([col + ' = ' + quote(vals[index]) + ',' for index, col in enumerate(cols)])
    cols = cols[:len(cols) - 1]

    return cols


def check_table(model):
    tb = model.table
    c = sqlite3.connect('db.sqlite3')
    sql = 'CREATE TABLE  IF NOT EXISTS {} '.format(tb)
    cols = model.data.keys()
    sql += " ("
    for col in cols:
        if col == 'id':
            sql += col + ' INT PRIMARY KEY,'
        else:

            sql += col + ' TEXT,'
    sql = sql[:len(sql) - 1]
    sql += ')'

    c.execute(sql)
    c.commit()
    c.close()


def run_query(sql):
    c = sqlite3.connect('db.sqlite3')
    c.execute(sql)
    c.commit()
    c.close()


# Updates columns of specified row
def update(table, r_cols, r_vals, where_condition='', where_val='', extra_sql=''):
    if len(r_cols) != len(r_vals):

        raise Exception("Not matching columns to values, {} columns {} values".format(len(r_cols), len(r_vals)))
    else:
        sql = 'UPDATE ' + table + ' SET '
        params = compile_basic_params(r_cols, r_vals)

        sql += params + ' '
        if where_condition != '' and where_val != '':
            where_condition = 'WHERE ' + where_condition + ' = ' + where_val

        sql += where_condition + ' ' + extra_sql

        run_query(sql)


def get_column_names(table, c):
    cur = c.execute('select * from ' + table)
    names = [desc[0] for desc in cur.description]
    return names


def __rechunk(data, rows=10000):
    for i in range(0, len(data), rows):
        yield data[i:i + rows]
    # used to re-chunk array into splitNum nths divisions


def __insert_all(models_, cur, sql):
    models_values = [list(model.data.values()) for model in models_]  # retrieve all data params from models

    if len(models_values) > 1000:
        models_chunked = list(__rechunk(models_values, 1000))  # Split each row into 1000 rows each list
        models_values.clear()

        for data in models_chunked:

            cur.execute('BEGIN TRANSACTION')

            for row in data:
                cur.execute(sql, row)
            cur.execute('COMMIT')
    else:
        cur.execute('BEGIN TRANSACTION')

        for row in models_values:
            cur.execute(sql, row)

        cur.execute('COMMIT')


def get_sql_vals(record):
    vals = ''
    vals += '('
    for val in record.data.keys():
        vals += val + ','

    vals = vals[:len(vals) - 1]

    vals += ')'

    return vals


def compile_insert_sql(insert_method, table, model_record):
    marks = ['?' for x in range(len(model_record.getVals()))]
    params = ','.join(marks)
    val_names = get_sql_vals(model_record)

    return insert_method + ' into {} {} values({}) '.format(table, val_names, params)


# gets model details from model
def __init_model(model_record):
    tb = model_record.table
    check_table(model_record)
    return model_record, tb


def add_models(models_):
    # data is modeled by first entry in list

    # multi use for single and multi inserts
    if isinstance(models_, DbModelR):
        models_ = [models_]
    elif len(models_) == 0:
        return

    model_record, table = __init_model(models_[0])
    sql = compile_insert_sql('insert or replace ', table, model_record)

    c = sqlite3.connect('db.sqlite3')
    cur = c.cursor()

    __insert_all(models_, cur, sql)

    c.close()


# Where conditional find
def find(table, condition_val, condition='id', additional_trail_sql=''):
    sql = 'Select * from ' + table + ' where {} = {} '.format(condition, condition_val)
    sql += additional_trail_sql

    return fetch_items(table, sql)


def get_last_id(model):
    c = sqlite3.connect('db.sqlite3')
    table = model.table
    cur = c.cursor()
    try:
        cur.execute('SELECT * FROM ' + table + ' ORDER BY id DESC LIMIT 1')
    except sqlite3.OperationalError:
        return '-1'

    records = cur.fetchall()
    if len(records) == 0:
        return '-1'
    id_ = str(records[0][model.getKeys().index('id')])
    # 'last id = ', id_)
    if (id_ is None):
        return '-1'
    elif id_.replace(' ', '') == '':
        return '-1'
    else:
        return id_


def fetch_items(table, sql):
    c = sqlite3.connect('db.sqlite3')
    cur = c.cursor()
    cur.execute(sql)
    names = get_column_names(table, c)

    records = cur.fetchall()

    records_converted = []
    data = {}

    for record in records:

        for index, name in enumerate(names):
            key = names[index]
            data[key] = str(record[index])
        new_dict = {}
        new_dict.update(data)

        records_converted.append(DbModelR(table, new_dict))

    c.close()
    return records_converted


def load_table_limit(table, limit, order='DESC'):
    sql = 'SELECT * FROM ' + table + ' ORDER BY id ' + order + ' LIMIT ' + str(limit)
    items = fetch_items(table, sql)
    return items


def load_table(table):
    sql = 'SELECT * FROM ' + table
    items = fetch_items(table, sql)
    return items


class DbModelR:
    def __init__(self, table, data, vals=None, use_id=True):
        self.table = table
        if vals is not None:
            self.data = {'id': ''}
            for index, col in enumerate(data):
                self.data[col] = vals[index]

        else:
            self.data = data
        if use_id:

            if (self.data.get('id') is None) or (self.data.get('id').replace(' ', '') == '') \
                    and (self.data['id']):
                self.data['id'] = 0

                id_ = get_last_id(self)

                id_ = str(int(id_) + 1)
                self.data['id'] = id_

    def getVals(self):
        return list(self.data.values())

    def getKeys(self):
        return list(self.data.keys())


def randstring(length):
    string = ''.join([random.choice(ascii_letters) for x in range(length)])

    return string


def __populate(table, col_a, row_a):
    datas = []
    names = []
    names.append('id')
    for i in range(col_a):
        names.append(randstring(20))
    vals = []
    id = 0

    for n in range(row_a):

        for i in range(len(names)):
            vals.append(str(random.randrange(1000)))
        vals[0] = str(id)

        id += 1
        datas.append(DbModelR(table, names, vals))
        vals.clear()

    add_models(datas)


# Used to populate a table with dummy data but with custom column names. And implements last_id for future expansion
def __populate_custom(table, cols, row_a):
    datas = []
    id = int(get_last_id(DbModelR(table, {})))
    data = {}

    for n in range(row_a):
        id += 1

        for i in cols:
            data[i] = str(random.randrange(1000))
        data['id'] = str(id)
        datas.append(DbModelR(table, data.copy(), id=False))

        data.clear()
    add_models(datas)


if __name__ == '__main__':
    pass
