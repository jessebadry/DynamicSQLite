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
    return DbModelR(table, data)


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


def get_sql_vals(record):
    vals = ''
    vals += '('
    for val in record.data.keys():
        vals += val + ','

    vals = vals[:len(vals) - 1]

    vals += ')'

    return vals


def run_query(sql):
    c = sqlite3.connect('db.sqlite3')
    c.execute(sql)
    c.commit()
    c.close()


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


def compile_insert_sql(insert_method, table, model_record):
    marks = ['?' for x in range(len(model_record.getVals()))]
    params = ','.join(marks)
    val_names = get_sql_vals(model_record)

    return insert_method + ' into {} {} values({}) '.format(table, val_names, params)


def __init_model(models):
    model_record = models[0]
    tb = model_record.table
    check_table(model_record)
    return model_record, tb


def add_models(models_):
    # data is modeled by first entry in list

    if isinstance(models_, DbModelR):
        models_ = [models_]
    elif len(models_) == 0:
        return

    model_record, table = __init_model(models_)
    sql = compile_insert_sql('insert or replace ', table, model_record)

    c = sqlite3.connect('db.sqlite3')
    cur = c.cursor()

    __insert_all(models_, cur, sql)

    c.close()


def find(table, condition_val, condition=None):
    if condition is None:
        condition = 'id'  # defaults id
    sql = 'Select * from ' + table + ' where {} = {}'.format(condition, condition_val)
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

    if (id_ is None) or id_.replace(' ', '') == '':
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
    for name in names:
        data[name] = None
    for record in records:

        for index, name in enumerate(names):
            key = names[index]
            data[key] = str(record[index])
        new_dict = {}
        new_dict.update(data)

        records_converted.append(DbModelR(table, new_dict))

    c.close()
    return records_converted


def load_table_limit(table, limit):
    sql = 'SELECT * FROM ' + table + ' ORDER BY id ASC LIMIT ' + str(limit)
    items = fetch_items(table, sql)
    return items


def load_table(table):
    sql = 'SELECT * FROM ' + table
    items = fetch_items(table, sql)
    return items


class DbModelR:
    def __init__(self, table, data, vals=None, id=True):
        self.table = table
        if vals is not None:
            self.data = {'id': ''}
            for index, col in enumerate(data):
                self.data[col] = vals[index]

        else:
            self.data = data
        if id:

            if (self.data.get('id') is None) or self.data.get('id').replace(' ', '') == '':
                self.data['id'] = 0

                id = str(int(get_last_id(self)) + 1)
                self.data['id'] = id

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
    # example of dynamic entry

    model = create_empty_model('Users', ['Name', 'Age', 'Score'])
    add_models(model)
