import os, base64

class SessionStore:

    def __init__(self):
        # a dictionary (of dictionaries)
        # keyed by: session ID
        self.sessions = {}
        return

    # METHODS

    # helper method
    def createSessionId(self):
        # using random to make it unguessable and (hopefully) unique
        # I probably should be signing this with a hashing Algorithm
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

    def createSession(self):
        sessionId = self.createSessionId()
        self.sessions[sessionId] = {}
        return sessionId

    def getSessionData(self, sessionId):
        if sessionId in self.sessions:
            return self.sessions[sessionId]
        else:
            return None
