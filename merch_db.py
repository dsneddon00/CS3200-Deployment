import os
import psycopg2
import psycopg2.extras
import urllib.parse

# attributes: title TEXT, genre TEXT, time INT, rating INT, views INT

'''
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
'''

class MerchDB:

    def __init__(self):
        #self.connection = sqlite3.connect("merch.db")
        #self.connection.row_factory = dict_factory
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        # a cursor is a pointer, a reference to somoe bigger thing
        self.cursor = self.connection.cursor()
        return

    def __del__(self):
        self.connection.close()

    def createMerchTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS merch (id SERIAL PRIMARY KEY, name VARCHAR(255), type VARCHAR(255), color VARCHAR(255), price INT, quantity INT)")
        self.connection.commit()

    def createLoginTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS login (id SERIAL PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
        self.connection.commit()

    def getAllMerch(self):
        # READ from the table
        self.cursor.execute("SELECT * FROM merch")

        merch = self.cursor.fetchall()

        return merch

    def getOneMerch(self, merch_id):
        # no string concatination may ever occur on a database query
        data = [merch_id]
        self.cursor.execute("SELECT * FROM merch WHERE id = %s", data)
        merch = self.cursor.fetchone()
        return merch # might return None if the result is empty

    def createMerch(self, name, type, color, price, quantity):
        # INSERT into the table
        data = [name, type, color, price, quantity]
        # %s is a placeholder, data bind will now occur for us
        # this prevents SQL injection, which can tear apart a database
        self.cursor.execute("INSERT INTO merch (name, type, color, price, quantity) VALUES (%s, %s, %s, %s, %s)", data)
        self.connection.commit()

    def updateMerch(self, merch_id, name, type, color, price, quantity):
        data = [name, type, color, price, quantity, merch_id]

        self.cursor.execute("UPDATE merch SET name = %s, type = %s, color = %s, price = %s, quantity = %s WHERE id = %s", data)
        self.connection.commit()

        #self.cursor.execute("UPDATE merch SET")
        #data [..., ..., id_at_the_end]
        #self.cursor.execute("UPDATE pies SET flavor = %s, crust = %s WHERE id = %s"", data)
        return

    def deleteMerch(self, video_id):
        data = [video_id]
        self.cursor.execute("DELETE FROM merch WHERE id = %s", data)
        self.connection.commit()

    def getAllLogin(self):
        # READ from the table
        self.cursor.execute("SELECT * FROM login")

        login = self.cursor.fetchall()

        return login

    def getOneLogin(self, login_id):
        # no string concatination may ever occur on a database query
        data = [login_id]
        self.cursor.execute("SELECT * FROM login WHERE id = %s", data)
        login = self.cursor.fetchone()
        return login # might return None if the result is empty

    def createLogin(self, username, password):
        # INSERT into the table
        data = [username, password]
        # %s is a placeholder, data bind will now occur for us
        # this prevents SQL injection, which can tear apart a database
        self.cursor.execute("INSERT INTO login (username, password) VALUES (%s, %s)", data)
        self.connection.commit()

    def updateLogin(self, login_id, username, password):
        data = [username, password]

        self.cursor.execute("UPDATE login SET username = %s, password = %s WHERE id = %s", data)
        self.connection.commit()

        #self.cursor.execute("UPDATE login SET")
        #data [..., ..., id_at_the_end]
        #self.cursor.execute("UPDATE pies SET flavor = %s, crust = %s WHERE id = %s"", data)
        return

    def deleteLogin(self, video_id):
        data = [video_id]
        self.cursor.execute("DELETE FROM login WHERE id = %s", data)
        self.connection.commit()

    def findUser(self, username):
        print("Username: ", username)
        data = [username]
        self.cursor.execute("SELECT * FROM login WHERE username = %s", data)
        checkUser = self.cursor.fetchone()
        return checkUser
