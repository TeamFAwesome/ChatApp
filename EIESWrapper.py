import requests,json,time,datetime

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
    def __init__(self):
        global urlprefix
        self.baseUrl='%s/api/v1/' % urlprefix

    def __exec(self, operation, page, args):
        url = "%s%s" % (self.baseUrl, page)
        return operation(url, data=json.dumps(args), headers={'content-type': 'application/json'})
        
    def __login(self, operation, args):
        return self.__exec(operation, 'login', args)

    ### BEGIN SESSION
    def Login(self, email, password):
        res = self.__login(requests.post, {'email': email, 'password': password})
        # TODO: HANDLE RESULT, populate class variables, return boolean for success
        return res

    def Logout(self):
        return requests.delete("%s%s" % (self.baseUrl, 'login'))
    ### END SESSION
        
        
    ### BEGIN USER INFO STUFF
    def GetUserInfo(self, user_id, session_id):
        return self.__exec(requests.get, 'users/%d' % user_id, {'session_id': session_id})
    ### BEGIN USER INFO STUFF
    
    
    ### BEGIN KEY STUFF
    def LookupPubKey(self, domain, port):
        return self.__exec(requests.get, 'public_keys', {'domain': domain, 'port': port})
    
    def NewKey(self, session_id, name, body):
        return self.__exec(requests.post, 'keys', {'session_id': session_id, 'name': name, 'body': body})
        
    def RetrieveKey(self, key_id, session_id):
        return self.__exec(requests.get, 'keys/%d' % key_id, {'session_id': session_id})
    
    def UpdateKey(self, session_id, name, body):
        return self.__exec(requests.put, 'keys', {'session_id': session_id, 'name': name, 'body': body})
        
    def DestroyKey(self, key_id, session_id):
        return self.__exec(requests.delete, 'keys/%d' % key_id, {'session_id': session_id})
    ### END KEY STUFF
    
    
    ### BEGIN ENTITY STUFF
    def NewEntity(self, session_id, name, domain, port):
        return self.__exec(requests.post, 'entities', {'session_id': session_id, 'name': name, 'domain': domain, 'port': port})
        
    def RetrieveEntity(self, entity_id, session_id):
        return self.__exec(requests.get, 'entities/%d' % entity_id, {'session_id': session_id})
    
    def UpdateEntity(self, session_id, name, domain, port):
        return self.__exec(requests.put, 'entities', {'session_id': session_id, 'name': name, 'domain': domain, 'port': port})
        
    def DestroyEntity(self, entity_id, session_id):
        return self.__exec(requests.delete, 'entities/%d' % entity_id, {'session_id': session_id})
    ### END ENTITY STUFF
    

    ### BEGIN ENTITY TOKEN STUFF
    def CreateEntityToken(self, session_id, entity_id, key_id):
        return self.__exec(requests.post, 'entity_tokens', {'session_id': session_id, 'entity_id': entity_id, 'key_id': key_id})
        
    def RetrieveEntity(self, token_id, session_id):
        return self.__exec(requests.get, 'entity_tokens/%d' % token_id, {'session_id': session_id})
    
    def DestroyEntity(self, token_id, session_id):
        return self.__exec(requests.delete, 'entities_tokens/%d', {'session_id': session_id})
    ### END ENTITY TOKEN STUFF