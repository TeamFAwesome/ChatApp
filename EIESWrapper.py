#!/usr/bin/python2 -i
import requests,json,time,datetime

debug = False #True

def typeRighter(val):
    try:
        return float(val)
    except:
        pass
    try:
        return int(val)
    except:
        pass
    return val

def typeRightArr(arr):
    return [typeRighter(x) for x in arr]

urlprefix = "https://eies.herokuapp.com"
    
class EIESWrapper:
    def __init__(self, url=None):
        global urlprefix
        if url != None:
            urlprefix = url
        self.baseUrl='%s/api/v1/' % urlprefix
        if debug:
            print "Using %s as base URL for API calls" % self.baseUrl
        self.user_id = None
        self.session_id = None
        self.session = requests.Session()

    def __exec(self, operation, page, args):
        global debug
        url = "%s%s" % (self.baseUrl, page)
        if debug:
            import urllib
            print "%s %s?%s" % (operation.__name__.upper(), url, urllib.urlencode(args))
        res = operation(url, data=json.dumps(args), headers={'content-type': 'application/json'})
        if debug:
            jsonmaybe = None
            try:
                jsonmaybe = str(res.json())
            except:
                jsonmaybe = "NOT JSON?"
            print "%s\t%s" % (str(res), jsonmaybe)
        return res

    ### BEGIN SESSION
    def Login(self, email, password):
        res = self.__exec(self.session.post, 'login', {'email': email, 'password': password})
        if int(res.status_code) != 200:
            res.close()
            return False
        self.user_id = res.json()['user_id']
        self.session_id = res.json()['session_id']
        return True

    def Logout(self):
        res = self.session.delete("%s%s" % (self.baseUrl, 'login'))
        if int(res.status_code) != 204:
            print res
            return False
        self.session.close()
        EIESWrapper.__init__(self) #reset all the things
        return True
        
    ### END SESSION
        
        
    ### BEGIN USER INFO STUFF
    def GetUserInfo(self):
        return self.__exec(self.session.get, 'users/%d.json' % self.user_id, {'session_id': self.session_id})
    ### BEGIN USER INFO STUFF
    
    
    ### BEGIN KEY STUFF
    def LookupPubKey(self, domain, port):
        return self.__exec(self.session.get, 'public_keys', {'domain': domain, 'port': port})
    
    def NewKey(self, name, body):
        return self.__exec(self.session.post, 'keys', {'session_id': self.session_id, 'name': name, 'body': body})
        
    def RetrieveKey(self, key_id):
        return self.__exec(self.session.get, 'keys/%d' % key_id, {'session_id': self.session_id})
    
    def UpdateKey(self, name, body):
        return self.__exec(self.session.put, 'keys', {'session_id': self.session_id, 'name': name, 'body': body})
        
    def DestroyKey(self, key_id):
        return self.__exec(self.session.delete, 'keys/%d' % key_id, {'session_id': self.session_id})
    ### END KEY STUFF
    
    
    ### BEGIN ENTITY STUFF
    def NewEntity(self, name, domain, port):
        return self.__exec(self.session.post, 'entities', {'session_id': self.session_id, 'name': name, 'domain': domain, 'port': port})
        
    def RetrieveEntity(self, entity_id):
        return self.__exec(self.session.get, 'entities/%d' % entity_id, {'session_id': self.session_id})
    
    def UpdateEntity(self, name, domain, port):
        return self.__exec(self.session.put, 'entities', {'session_id': self.session_id, 'name': name, 'domain': domain, 'port': port})
        
    def DestroyEntity(self, entity_id):
        return self.__exec(self.session.delete, 'entities/%d' % entity_id, {'session_id': self.session_id})
    ### END ENTITY STUFF
    

    ### BEGIN ENTITY TOKEN STUFF
    def CreateEntityToken(self, entity_id, key_id):
        return self.__exec(self.session.post, 'entity_tokens', {'session_id': self.session_id, 'entity_id': entity_id, 'key_id': key_id})
        
    def RetrieveEntity(self, token_id, session_id):
        return self.__exec(self.session.get, 'entity_tokens/%d' % token_id, {'session_id': self.session_id})
    
    def DestroyEntity(self, token_id, session_id):
        return self.__exec(self.session.delete, 'entities_tokens/%d', {'session_id': self.session_id})
    ### END ENTITY TOKEN STUFF

if __name__ == "__main__":
    import sys
    eies = None
    if len(sys.argv) > 1:
       eies = EIESWrapper(url=sys.argv[1])
    else:
       eies = EIESWrapper()
    email = raw_input('email: ')
    password = raw_input('password: ')
    if email != None and len(email) > 0 and password != None and len(password) > 0:
        print "Object \"eies\" initialized. Now calling eies.Login with your username and password. Good luck!"
        eies.Login(email, password)
