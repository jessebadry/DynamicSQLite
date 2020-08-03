from DynamicSQLite import database
from DynamicSQLite.database import DModel
class Customer(DModel):
    TABLE = 'Customers'
    def __init__(self, name, address):
        self.name = name
        self.address = address
        super(Customer, self).__init__(TABLE, self.__dict__.copy())



new_customer = Customer('Jesse', '201 Fredrick Avenue')
database.add_models(new_customer)


customers = database.load_table_limit(Customer.TABLE, 2)
print(customers)

