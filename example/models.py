from database import DbModelR
import database

# Example usage for initializing defined models for an application

# this class initializes models used in the application for connectivity with Database


CustomerNames = ['id', 'firstName', 'lastName', 'company', 'mailAddress',
                 'streetAddress', 'city', 'state_province', 'zip',
                 'country', 'phone', 'workPhone', 'taxID', 'fax',
                 'email', 'nameOrCompany']

InvoiceNames = ['id', 'carModel', 'manufacturer', 'vin', 'condition', 'licenseState', 'regNum', 'stage',
                'vehicleID', 'paintCode', 'bodyStyle', 'year', 'dateOfInvoice', 'transmission', 'driveSystem',
                'primaryColor', 'twoToneColor', 'underHood', 'interiorTrimCode', 'engineType', 'exteriorTrimCode',
                'stripeCode', 'bodyRate', 'frameRate', 'mechRate', 'paintRate', 'refinishRate', 'shopSupplies',
                'gstTax',
                'pstTax', 'claimant', 'policyNumber', 'claimNumber', 'inspectionSite', 'dateOfLoss', 'shopFacility',
                'daysToRepair', 'estimator', 'typeOfLoss', 'insuranceCompany', 'discount', 'deductible',
                'insured', 'customerID']

PartNames = ['id', 'operation', 'position', 'part', 'labourHours', 'type', 'exteriorStage',
             'interiorStage', 'booleangst', 'booleanpst', 'stageSettings', 'price', 'refinishTime', 'other', 'quantity',
             'note', 'invoiceID']

VehicleNames = ['carModel', 'manufacturer', 'vin', 'condition', 'licenseState', 'regNum', 'stage',
                'vehicleID', 'paintCode', 'bodyStyle', 'year', 'dateOfInvoice', 'engineType', 'transmission',
                'driveSystem', 'primaryColor', 'twoToneColor', 'underHood', 'interiorTrimCode', 'exteriorTrimCode',
                'stripeCode'
                ]  # Composite model


def check_all_models():
    database.check_table(database.create_empty_model('Invoices', InvoiceNames))
    database.check_table(database.create_empty_model('Customers', CustomerNames))
    database.check_table(database.create_empty_model('Parts', PartNames))


class InvoiceObj(DbModelR):
    class Vehicle(DbModelR):
        def __init__(self, data):
            table = None  # class is internal model
            super(self.__class__, self).__init__(table, data)
            for key in VehicleNames:  # finds data linked to vehicle model names
                self.data[key] = self.data[key]

    def __init__(self, data, customerData):
        table = 'Invoices'
        super(self.__class__, self).__init__(table, data)
        self.customer = None
        self.__displayNames = ['firstName', 'lastName', 'mailAddress',
                               'manufacturer', 'carModel', 'vin']
        self.customerData = dict
        self.displays = {}  # displayable data for table
        self.vehicle = self.Vehicle(self.data)
        self.setCustomerData(customerData)

    def setCustomerData(self, customer):

        self.customer = customer
        merged = {}
        if customer is not None:
            merged.update(self.customer.data)
        merged.update(self.data)
        # adding customer displayables to invoice displayables
        for name in self.__displayNames:
            self.displays[name] = merged[name]

    def initInteralModel(self):
        pass

    def get_columns(self):
        return list(self.displays.keys())

    def get_vals(self):
        return list(self.displays.values())


class Customer(DbModelR):
    def __init__(self, data):
        table = 'Customers'
        super(self.__class__, self).__init__(table, data)

        self.customerData = dict
        self.displays = {}
        self.__displayNames = ['firstName', 'lastName', 'mailAddress']
        self.set_data(self.data)

    def set_data(self, data_dict):
        self.data = data_dict
        for name in self.__displayNames:
            self.displays[name] = self.data[name]

    def get_columns(self):
        return list(self.displays.keys())

    def get_vals(self):
        return list(self.displays.values())


check_all_models()
