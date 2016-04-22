#!/usr/bin/env python3

#
#       Eric McCann 2016
#

import os,sys,getopt,traceback,subprocess,re
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import codecs
from Common import *
printerer.Instance().setPrefixer() #singleton for prefixing prints with file and number

import json

class KeyHelperRuntimeHandler:
    def __init__(self):
        self.identity_file = None
        self.public_key_filename_format = "%s.pub"
        self.private_key_filename_format = "%s.pem"
        self.private_file = self.private_key_filename_format % self.identity_file
        self.public_file = self.public_key_filename_format % self.identity_file
        self.private_key = None
        self.private_key_text = None
        self.public_key = None
        self.verbose = False

    def ShowUsage(self):
        realprint("%s -k IDENTITY_FILE [-v] [-h]\n\
\t-k IDENTITY_FILE          read private key from IDENTITY_FILE\n\
\t                          and public key from IDENTITY_FILE.pub\n\
\t                          (similar to ssh's -k behavior)\n\
\n\
\t-v                        enable verbose output\n\
\n\
\t-h                        display this text" % (sys.argv[0]), file=sys.stderr);

    def SetIdentityFileName(self, filename="~/.chatapp_key"):
        self.identity_file = os.path.expanduser(filename)
        self.private_file = self.private_key_filename_format % self.identity_file
        self.public_file = self.public_key_filename_format % self.identity_file
        if self.verbose:
            print("Using identity_file: %s" % self.identity_file)

    def Init(self):
        # read and handle options
        try:
            opts, extraparams = getopt.getopt(sys.argv[1:], "k:vh") #start at the second argument.
        except getopt.GetoptError as err:
            #print error info and exit
            print(str(err), file=sys.stderr)
            realprint(traceback.format_exc(), file=sys.stderr)
            return 2
        for o,a in opts:
            if o == "-k":
                self.SetIdentityFileName(a)
            elif o == "-v":
                self.verbose = True
            else:
                self.ShowUsage()
                if o == "-h":
                    return 0
                return 1
        if __name__ == "__main__" and not self.identity_file:
            self.ShowUsage()
            return 1

        return

    def Read(self, filename, file_info_to_print = None):
        content = None
        if not file_info_to_print:
            file_info_to_print = ""
        else:
            file_info_to_print = " %s from" % file_info_to_print
        if self.verbose:
            print("Reading%s: %s" % (file_info_to_print,filename))
        try:
            with open(filename, 'r') as f:
                content = f.read()
                f.close()
            if self.verbose:
                print("Successfully read%s: %s" % (file_info_to_print, filename))
        except IOError as err:
            print("Failed to read%s: %s -- %s" % (file_info_to_print, filename, str(err)), file=sys.stderr)
            realprint(traceback.format_exc(), file=sys.stderr)
            return None
        except:
            print("Failed to read%s: %s" % (file_info_to_print, filename) , file=sys.stderr)
            realprint(traceback.format_exc(), file=sys.stderr)
            return None
        return content

    def Write(self, filename, contents, file_info_to_print=None):
        if not file_info_to_print:
            file_info_to_print = ""
        else:
            file_info_to_print = " %s to" % file_info_to_print
        if self.verbose:
            print("Writing%s: %s" % (file_info_to_print,filename))
        try:
            with open(filename, 'w') as content_file:
                content_file.write(contents)
                content_file.flush()
                content_file.close()
            if self.verbose:
                print("Successfully wrote%s: %s" % (file_info_to_print, filename))
        except IOError as err:
            print("Failed to write%s: %s -- %s" % (file_info_to_print, filename, str(err)), file=sys.stderr)
            realprint(traceback.format_exc(), file=sys.stderr)
            return False
        except:
            print("Failed to write%s: %s" % (file_info_to_print, filename) , file=sys.stderr)
            realprint(traceback.format_exc(), file=sys.stderr)
            return False
        return True

    def Load(self):
        # read the public and private key file if they exist
        if not os.path.exists(self.private_file) or not os.path.exists(self.public_file):
            print("One or more of the specified identity files does not exist", file=sys.stderr)
            return False

        # read private key
        self.private_key_text = self.Read(self.private_file, "private key")
        if self.private_key_text != None:
            self.private_key = RSA.importKey(bytes(self.private_key_text,'utf8'))

        # read public key
        self.public_key_text = self.Read(self.public_file, "public key")
        if self.public_key_text != None:
            self.public_key_text = RSA.importKey(bytes(self.public_key_text,'utf8'))

        if self.private_key and self.public_key:
            return True
        return False

    def Create(self):
        if self.private_file == None or self.identity_file == None or self.public_file == None:
            return False
        #http://stackoverflow.com/a/22449476
        key = RSA.generate(1024, os.urandom)
        self.private_key = key
        self.private_key_text = key.exportKey().decode('utf8')
        self.Write(self.private_file, self.private_key_text, "private key")
        os.chmod(self.private_file, 0o600)
        self.public_key = key.publickey()
        self.public_key_text = self.public_key.exportKey().decode('utf8')
        self.Write(self.public_file, self.public_key_text, "public key")
        return True

    def _getPrivateKey(self):
        return {"n": self.private_key.n, "e": self.private_key.e, "d": self.private_key.d, "text": self.private_key_text}

    def GetPrivateKey(self):
        return {"key": self._getPrivateKey()}

    def _getPublicKey(self):
        return {"n": self.public_key.n, "e": self.public_key.e, "text": self.public_key_text}

    def GetPublicKey(self):
        return {"key": self._getPublicKey()}

    def InterpretAndWritePrivate(self, textboxgarbage):
        try:
            priv = RSA.importKey(bytes(textboxgarbage,'utf8'))
            text = key.exportKey('PEM').decode('utf8')
            if self.Write(self.private_file, text, "private key"):
                self.private_key_text = text
                self.private_key = priv
                os.chmod(self.private_file, 0o600)
                return {"key": self._getPrivateKey()}
        except:
            noop=1
        return {"error": "Failed to interpret private key text!", "key": self._getPrivateKey()}

    def InterpretAndWritePublic(self, textboxgarbage):
        if self.Write(self.public_file, textboxgarbage, "public key"):
            self.public_key = textboxgarbage
            return {"key": self._getPublicKey()}
        return {"error": "Failed to interpret public key text!", "key": self._getPublicKey()}

    def RegenerateKeyPair(self):
        if self.Create():
            return {"public": self._getPublicKey(), "private": self._getPrivateKey()}
        return {"error": "Failed to create? somehow?", "public": self._getPublicKey(), "private": self._getPrivateKey()}

    def Encrypt(self, message, pubkey):
        keydata = bytes(pubkey, 'utf-8')
        key = RSA.importKey(keydata)
        return {"encrypted": codecs.encode(PKCS1_OAEP.new(key).encrypt(bytes(message,'utf-8')),'hex').decode('utf-8')}

    def Decrypt(self, message):
        decrypted = None
        try:
            decrypted = PKCS1_OAEP.new(self.private_key).decrypt(codecs.decode(bytes(message, 'utf-8'), 'hex')).decode('utf-8')
        except ValueError as err:
            print("Failed to decrypt message: %s" % str(err), file=sys.stderr)
            realprint(traceback.format_exc(), file=sys.stderr)
            return {"error": "Failed to decrypt message"}
        return {"decrypted": decrypted}

if __name__ == "__main__":
    import code
    impl = KeyHelperRuntimeHandler()
    errorcode = impl.Init()
    if errorcode:
        sys.exit(errorcode)
    #if init returned None, Load
    if not impl.Load():
        impl.Create()
    print(impl.GetPrivateKey())
    print(impl.GetPublicKey())
    code.interact(banner="Object \"impl\" initialized with current private and public keys... stored places. Good luck!",local=locals())
