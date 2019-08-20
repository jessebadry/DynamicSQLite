# DynamicSQLite
My Small SQLite Library, made so I never need to code this in python again. All entries and tables are made using Python Dictionaries.
Probably not the best but I found it useful maybe you will to.

Creating tables...
The Database on default creates an id (excluding the SQLite built in id) INT as the Primary Key for convenience, and generates 
the columns based on the model(DbModel which contains a dictionary) supplied.
Obviously the table system isn't neccesarily flexible yet, but could easily be so,
if you need more customization you are welcome to do so.



The Example directory shows how I  implemented the database, it was meant for basic user interaction, and built so I could 
quickly make new models without additional code, all data defaults to string except the id, you can change that if you feel fit.

I mainly made this so I never need to make SQLite boilerplate in Python again, or later easily expand this.


Do what ever you want with it, I don't care.
