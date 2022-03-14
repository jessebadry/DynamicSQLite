
DynamicSQLite is a light-weight (but very limited) ORM.

It's very limited as it's only supported data-type is strings, but is open for modification for data-conversion.

The default name is db.sqlite3,
which you can modify `DEFAULT_DB` within database.py


# Example
```python
from DynamicSQLite import database
from DynamicSQLite.database import DModel
class Customer(DModel):
    TABLE = 'Customers'
    def __init__(self, name, address):
        self.name = name
        self.address = address
        super(Customer, self).__init__(self.TABLE, self.__dict__.copy())



new_customer = Customer('Jesse', '201 Fredrick Avenue')
database.add_models(new_customer)


customers = database.load_table_limit(Customer.TABLE, 2)
print(customers)
```
