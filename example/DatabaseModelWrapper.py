import database
import models


# Wrapper for the dynamo database
def __populate_invoices():
    database.__populate_custom('Invoices', models.InvoiceNames, 100)


def get_invoices(limit):
    invoices_raw = database.load_table_limit('Invoices', limit)  # loads raw DBModels
    invoices = []
    for invoice in invoices_raw:
        # finds associated customer
        customers = database.find('Customers', invoice.data['customerID'])
        customer = None
        if len(customers) != 0:
            customer = customers[0]

        invoices.append(models.InvoiceObj(invoice.data,customer))

    return invoices


def get_parts(invoice):
    parts = database.find('Parts', invoice.data['id'], 'invoiceID')
    return parts


def last_id(table, where, where_val, *conditions):
    sql = 'Select * from {} WHERE {} = {} ORDER BY  '.format(table, where, where_val)

    length = len(conditions)
    for index, condition in enumerate(conditions):
        sql += condition
        if index != length:
            sql += ' DESC'
            if index != length - 1:
                sql += ','
            else:
                sql += ';'

    print(sql)

    items = database.fetch_items(table, sql)
    if len(items) == 0:
        return '-1'

    return items[0].data['id']


def delete_item(table, conditions):
    sql = 'DELETE FROM {} WHERE {}'.format(table, conditions)

    database.run_query(sql)


def save(model):
    database.add_models(model)


def get_customers(limit):
    customers = [models.Customer(cust.data)
                 for cust in database.load_table_limit('Customers', limit)]

    return customers


if __name__ == '__main__':
    print(last_id('Parts', 'invoiceID', '0', 'id'))
