from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
from urllib.parse import parse_qs
import json
import sys
from merch_db import MerchDB
from passlib.hash import bcrypt
from sessionStore import SessionStore


gSessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):

    # cookie and session stuff
    def loadCookie(self):
        # read the Cookie header
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
            print("Cookie from client:", self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()
            print("No cookie for you, frowny face")
        # save for later

    def sendCookie(self):
        # send one or more Set-Cookie headers TO client
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())

    def loadSession(self):
        self.loadCookie() # find cookie data inside self.cookie
        # step 1: check session ID is in the cookie?
        if 'sessionId' in self.cookie:
            # if session ID does exist:
            # load session data from session store using session ID
            sessionId = self.cookie['sessionId'].value
            self.sessionData = gSessionStore.getSessionData(sessionId)
            # if session data (emphasis on data) does not exist:
            if self.sessionData == None:
                # create a new session ID
                sessionId = gSessionStore.createSession()
                # create a new entry in the session store
                self.sessionData = gSessionStore.getSessionData(sessionId)
                # assign the new session ID into the cookie
                self.cookie['sessionId'] = sessionId
        # else:
        else:
            # create a new session ID
            sessionId = gSessionStore.createSession()
            # create a new entry in session store
            self.sessionData = gSessionStore.getSessionData(sessionId)
            # assign the new session ID into the cookie
            self.cookie['sessionId'] = sessionId

    def end_headers(self): #overridden from BaseHTTPRequestHandler
        self.sendCookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        # some CORS stuff coming soon
        BaseHTTPRequestHandler.end_headers(self) # call the original end_headers()

    def handleNotFound(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not found.", "utf-8"))

    def handleUsersRetrieveUser(self):
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        password = parsed_body["password"][0]
        username = parsed_body["username"][0]
        db = MerchDB()
        #1: find user in DB by username
        user = db.findUser(username)
        # if user exists:
        if user != None:
            # 2: verify password
            passwordHash = user["password"]
            # if match:
            if bcrypt.verify(password, passwordHash):
                # SUCCESS!
                # 201 status response
                self.send_response(201)
                # save user ID into the session data
                # self.sessionData["userId"] = user["id"]
                self.sessionData["userId"] = user["id"]
                print(self.sessionData)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(bytes(json.dumps(user), "utf-8"))
                # else:
            else:
                # :(
                print("Can't sign in, password is incorrect.")
                self.handle401()
                #else:
        else:
            # :(
            print("Can't sign in, user does not exisit")
            self.handle401()












# handle methods
    def handleListMerch(self):
        # IF YOU'RE NOT LOGGED IN, GO AWAY
        if "userId" not in self.sessionData:
            self.handle401()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")

        self.end_headers()

        # opening up the database and retrieve all of the merch
        db = MerchDB()
        allRecords = db.getAllMerch()
        self.wfile.write(bytes(json.dumps(allRecords), "utf-8"))

    def handleListLogin(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # opening up the database and retrieve all of the merch
        db = MerchDB()
        allRecords = db.getAllLogin()
        self.wfile.write(bytes(json.dumps(allRecords), "utf-8"))

    def handleRetrieveMerch(self, merch_id):
        if "username" not in self.sessionData:
            self.handle401()
            return
        elif self.path == "/merch":
            db = MerchDB()
            merchRecord = db.getOneMerch(merch_id)
            if merchRecord != None:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(bytes(json.dumps(merchRecord), "utf-8"))
            else:
                self.handleNotFound()

    def handleDeleteMerch(self, merch_id):
        db = MerchDB()
        merchRecord = db.getOneMerch(merch_id)

        if merchRecord != None:
            # DELETE THE merch HERE!!
            db.deleteMerch(merch_id)
            self.send_response(200)
            self.end_headers()
        else:
            self.handleNotFound()


# post methods

    def handleCreateMerch(self):
        if "userId" not in self.sessionData:
            self.handle401()
            return
        elif self.path == "/merch":
            length = int(self.headers["Content-Length"])
            request_body = self.rfile.read(length).decode("utf-8")
            print("the request body:", request_body)
            parsed_body = parse_qs(request_body)
            # pesky index 0 cause these are arrays
            name = parsed_body['name'][0]
            type = parsed_body['type'][0]
            color = parsed_body['color'][0]
            price = parsed_body['price'][0]
            quantity = parsed_body['quantity'][0]

            db = MerchDB()
            db.createMerch(name, type, color, price, quantity)

            self.send_response(201)
            self.end_headers()
    # registration
    def handleCreateLogin(self):
        length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(length).decode("utf-8")
        print("the request body:", request_body)
        parsed_body = parse_qs(request_body)
        username = parsed_body["username"][0]
        password = parsed_body["password"][0]

        h = bcrypt.hash(password)
        print("Creating", username)

        db = MerchDB()
        check = db.findUser(username)
        if check is not None:
            print("User already exists")
            self.send_response(422)
        else:
            db.createLogin(username, h)
            self.send_response(201)
            self.end_headers()
        '''
        db = LoginDB()
        if(db.getOneLogin(username) == None):
            self.send_response(201)
            self.end_headers()
            en_pass = bcrypt.hash(password)
            db.createLogin(username, en_pass)
        else:
            self.send_response(422)
            self.end_headers()
            self.wfile.write(bytes("Not validated.", "utf-8"))
        '''

    def handleUpdateMerch(self, merch_id):
        length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(length).decode("utf-8")
        print("the request body:", request_body)
        parsed_body = parse_qs(request_body)
        # todo figure out how to actually update the thing
        db = MerchDB()

        merch_name = parsed_body['name'][0]
        merch_type = parsed_body['type'][0]
        merch_color = parsed_body['color'][0]
        merch_price = parsed_body['price'][0]
        merch_quantity = parsed_body['quantity'][0]

        merchMember = db.getOneMerch(merch_id)
        if merchMember:
            db.updateMerch(merch_id, merch_name, merch_type, merch_color, merch_price, merch_quantity)
            self.send_response(201)
            self.end_headers()
        else:
            self.handleNotFound()




    def do_OPTIONS(self):
        self.loadSession()
        #if self.path == "/merch":
        # part of the pre-flight requests
        self.send_response(204)
        # methods would include, GET, POST, PUT, DELETE, OPTIONS
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()

    def do_GET(self):
        self.loadSession()
        # this is an incoming GET request
        # what about the path??
        print("The request path is", self.path)
        # get the path parts and make them readable to the server
        path_parts = self.path.split('/')
        collection = path_parts[1]
        if len(path_parts) > 2:
            member_id = path_parts[2]
        else:
            member_id = None

        # we need this part for update and delete as well, keep in mind
        # check path and handle them accordingly
        if collection == "merch":
            if member_id:
                self.handleRetrievemerch(member_id)
            else:
                self.handleListMerch()

        elif collection == "login":
            user = self.sessionData
            self.handleListLogin()
        else:
            self.handleNotFound()

        """
        elif self.path == "/merch/????":
            self.handleRetrievemerch()
        else:
            self.handleNotFound()
        """
    def do_POST(self):
        self.loadSession()
        if self.path == "/merch":
            self.handleCreateMerch()
        elif self.path == "/login":
            self.handleCreateLogin()
        elif self.path == "/sessions":
            self.handleUsersRetrieveUser()
        else:
            self.handleNotFound()

    def do_DELETE(self):
        self.loadSession()
        path_parts = self.path.split('/')
        collection = path_parts[1]
        if len(path_parts) > 2:
            member_id = path_parts[2]
        else:
            member_id = None

        # we need this part for update and delete as well, keep in mind
        # check path and handle them accordingly
        if collection == "merch":
            if member_id:
                self.handleDeleteMerch(member_id)
            else:
                self.handleNotFound()
        else:
            self.handleNotFound()

    def do_PUT(self):
        self.loadSession()
        path_parts = self.path.split('/')
        collection = path_parts[1]
        if len(path_parts) > 2:
            member_id = path_parts[2]
        else:
            member_id = None

        if collection == "merch" and member_id:
            self.handleUpdateMerch(member_id)
        else:
            self.handleNotFound()
        '''
        if self.path == "/merch":
            continue
            #self.handleUpdateMerch()
        else:
            self.handleNotFound()
        '''

    def handle401(self):
        self.send_response(401)
        self.end_headers()
        self.wfile.write(bytes("Not authorized.", "utf-8"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass # nothing to see here

def run():

    # Create any DB table, if they don't already exist, and then
    # disconnect from the DB
    db = MerchDB()
    db.createMerchTable()
    db.createLoginTable()
    db = None # disconnect
    # the main function
    # boots up the server and wait for incoming requests
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    # http port number is 8080
    listen = ("0.0.0.0", port)
    server = ThreadedHTTPServer(listen, MyRequestHandler)
    print("The server is running!")
    server.serve_forever()
    print("This will never , ever execute.")

run()
