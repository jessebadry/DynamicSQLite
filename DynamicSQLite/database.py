import sqlite3
import random
import re
from logging import warning
from string import ascii_letters

DEFAULT_DB = 'db.sqlite3'


def create_empty_model(table, *columns):
    if isinstance(columns[0], list):
        columns = columns[0]
    data = {}
    for col in columns:
        data[col] = ''
    return DModel(table, data, use_id=False)


def empty_dict(cols):
    data = {}
    for col in cols:
        data[col] = ''
    return data


def quote(string):
    return '\'' + string + '\''


def remove_model(model):
    c = sqlite3.connect(DEFAULT_DB)
    sql = 'delete from {} WHERE id = {}'.format(model.table, model.data['id'])
    c.execute(sql)
    c.commit()
    c.close()


# basic params for SQLite e.g (update movies SET author = Jeff, producer  = Leonard ect..)
def compile_basic_params(cols, vals, delim=','):
    cols = ''.join([col + ' = ' + quote(vals[index]) + delim for index, col in enumerate(cols)])
    cols = cols[:len(cols) - len(delim)]

    return cols


# Parse Selection  values from sql string
def parse_values_fsql(sql):
    Lsql = sql.lower()
    final = sql[Lsql.index('select') + 6: Lsql.index('from')].replace(' ', '')

    matches = re.findall(r'(?:,|^)([a-zA-Z0-9*]*)', final)

    return matches


def check_table(model):
    tb = model.table
    c = sqlite3.connect(DEFAULT_DB)
    sql = 'CREATE TABLE  IF NOT EXISTS {} '.format(tb)
    cols = model.data.keys()
    sql += " ("
    for col in cols:
        col = col.replace(' ', '')

        if col == 'id':
            sql += col + '  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
        else:
            sql += col + ' TEXT,'
    sql = sql[:len(sql) - 1]
    sql += ')'
    c.execute(sql)
    c.commit()
    c.close()


def run_query(sql):
    c = sqlite3.connect(DEFAULT_DB)
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


# Requires active connection to database
def get_column_names(table, c, sql):
    values = parse_values_fsql(sql)

    cur = c.execute('select * from ' + table)
    names = [desc[0] for desc in cur.description]
    if values[0].replace(' ', '') == '*':
        return names
    else:
        names = [name for name in names if name in values]
    return names


def __rechunk(data, rows=10000):
    for i in range(0, len(data), rows):
        yield data[i:i + rows]
    # used to re-chunk array into splitNum nths divisions


def __insert_all(models_, cur, sql):
    models_values = [m.getVals() for m in models_]

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
    keys = list(record.data.keys())
    warning_bool = False
    id_missing = False

    if not ('id' in keys):
        keys.append('id')
        id_missing = True

    vals = ''
    vals += '('
    for val in keys:
        if ' ' in val:
            val = val.replace(' ', '')
            warning_bool = True

        vals += val + ','

    vals = vals[:len(vals) - 1]

    vals += ')'
    if warning_bool:
        warning(
            'Using Special Characters is not supported in SQLite Columns, and therefore not wrapped within \n'
            'DSQLite, Spaces will be replaced with null, making model keys without spaces. ')
    return vals, id_missing


def compile_insert_sql(insert_method, table, model_record):
    marks = ['?' for x in range(len(model_record.getVals()))]
    params = ','.join(marks)
    val_names, id_missing = get_sql_vals(model_record)
    if id_missing:
        raise Exception("Error in Compiling DSQl Query. id is missing from {}".format(model_record))
    return (insert_method + ' into {} {} values({}) '.format(table, val_names, params)), id_missing


# gets model details from model then initializes table if does not exist
def __init_model(model_record):
    tb = model_record.table
    check_table(model_record)
    return model_record, tb


def add_models(models_):
    # data is modeled by first entry in list

    # multi use for single and multi inserts
    if isinstance(models_, DModel):
        models_ = [models_]
    elif len(models_) == 0:
        return

    model_record, table = __init_model(models_[0])
    sql, id_missing = compile_insert_sql('insert or replace ', table, model_record)

    c = sqlite3.connect(DEFAULT_DB)
    cur = c.cursor()

    __insert_all(models_, cur, sql)

    c.close()


# Where conditional find
# Simple 1 condition find
def find(table, condition_val, condition='id', additional_trail_sql=''):
    sql = 'Select * from ' + table + ' where {} = \'{}\' '.format(condition, condition_val)
    sql += additional_trail_sql
    return fetch_items(sql)


def where(find_dict, table):
    sql = 'Select * from ' + table + ' Where ' + compile_basic_params(list(find_dict.keys()), list(find_dict.values()),
                                                                      delim=' AND ')

    return fetch_items(sql)


def get_last_id(model):
    c = sqlite3.connect(DEFAULT_DB)
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
    if id_ is None:
        return '-1'
    elif id_.replace(' ', '') == '':
        return '-1'
    else:
        return id_


# Core function of loading tables in DynamicSQLite
def fetch_items(sql, callback=None, call_back_params=None, single=False):
    using_callback = callable(callback)

    sql += " "  # Sanity check
    find_table = re.compile(r'(?<=from)\s+(.*?)(?=\s)', re.IGNORECASE)
    match = find_table.search(sql)
    if match is None:
        raise Exception("No Table Provided in SQL: ", sql)

    table = match.group(1)

    c = sqlite3.connect(DEFAULT_DB)
    cur = c.cursor()
    cur.execute(sql)
    __column_names = get_column_names(table, c, sql)

    records = cur.fetchall()
    records_converted = []

    data = {}  # Model Data Dictionary.

    for record in records:

        # Set Data for new dict
        for index, name in enumerate(__column_names):
            key = __column_names[index]
            data[key] = str(record[index])
        # Create new reference of dictionary for new object.
        model = DModel(table, data.copy())

        # Uses call back to determine new Model object THEN add to list.
        if using_callback:
            model = callback(call_back_params, model)  # Callbacks rely on them returning a DModel

        records_converted.append(model)

    c.close()
    if single and (len(records_converted) >= 1):
        return records_converted[0]
    elif single:
        return None
    return records_converted


def load_table_limit_call(table, limit, callback, order='DESC', call_back_params=None, sql=None):
    if not callable(callback):
        raise Exception(
            "Callback must be a  callable function, not {}"
            "\nFunction delegate = f(callback_params:dict,model:DModel)->DModel".format(
                type(callback).__name__))
    if not isinstance(sql, str):
        sql = 'select * from ' + table + ' order by id ' + order + ' limit ' + str(limit)

    items = fetch_items(sql, callback, call_back_params)
    return items


def load_table_limit(table, limit, order='DESC', sql=None):
    if not isinstance(sql, str):
        sql = 'SELECT * from ' + table + ' ORDER BY id ' + order + ' LIMIT ' + str(limit)
    items = fetch_items(sql)
    return items


def load_table(table):
    sql = 'select * from' + table
    items = fetch_items(sql)
    return items


class DModel:
    # use_id is deprecated and no longer used in any code
    def __init__(self, table, data, vals=None, use_id=None):
        self.table = table

        if vals is not None:
            self.data = {}
            for index, col in enumerate(data):
                self.data[col] = vals[index]

        else:
            self.data = {'id': None}
            self.data.update(data)

    def __str__(self):
        return "Model(Table->'{}'  Data: {}".format(self.table, self.data)

    def getVals(self):
        data = self.data.copy()
        if data.get('id') is not None:
            if data['id'].replace(' ', '') == '':
                data.pop('id')

        return list(self.data.values())

    def getKeys(self):
        return list(self.data.keys())


def randstring(length):
    string = ''.join([random.choice(ascii_letters) for x in range(length)])

    return string


def __debug_populate(table, col_a, row_a):
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
        datas.append(DModel(table, names, vals))
        vals.clear()

    add_models(datas)


# Used to populate a table with dummy data but with custom column names. And implements last_id for future expansion
def __debug_populate_custom(table: str, cols: list, row_a: int):
    datas = []
    data = {}

    for n in range(row_a):

        for i in cols:
            data[i] = str(random.randrange(1000))
        datas.append(DModel(table, data.copy()))

        data.clear()
    add_models(datas)
