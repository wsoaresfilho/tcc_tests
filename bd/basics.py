import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'tccbd'

config = {
    'user': 'tccadmin',
    'password': 'admin',
    'host': '127.0.0.1',
    'raise_on_warnings': True,
}

TABLES = {}
TABLES['user'] = (
    "CREATE TABLE `user` ("
    "  `user_no` int(11) NOT NULL AUTO_INCREMENT,"
    #"  `birth_date` date NOT NULL,"
    "  `username` varchar(30) NOT NULL,"
    "  `password` varchar(30) NOT NULL,"
    #"  `gender` enum('M','F') NOT NULL,"
    #"  `hire_date` date NOT NULL,"
    "  PRIMARY KEY (`user_no`)"
    ") ENGINE=InnoDB")


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        print("Database successfully created!")
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    print("Connection to BD successful!")
    cnx.database = DB_NAME
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist. It will now be created.")
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)

for name, ddl in TABLES.iteritems():
    try:
        print("Creating table {}: ".format(name)),
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
cnx.close()
