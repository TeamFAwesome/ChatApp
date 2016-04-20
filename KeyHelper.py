#!/usr/bin/env python3

#
#       Eric McCann 2016
#

import os,sys,getopt,traceback,subprocess,re
from Crypto.PublicKey import RSA

from Common import *
printerer.Instance().setPrefixer() #singleton for prefixing prints with file and number

class KeyHelperRuntimeHandler:
    def __init__(self):
        self.identity_file = os.path.expanduser("~/.chatapp_key")
        self.public_key_filename_format = "%s.pub"
        self.private_key_filename_format = "%s.pem"
        self.private_file = self.private_key_filename_format % self.identity_file
        self.public_file = self.public_key_filename_format % self.identity_file
        self.private_key = None
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
                self.identity_file = os.path.expanduser(a)
                self.private_file = self.private_key_filename_format % a
                self.public_file = self.public_key_filename_format % a
            elif o == "-v":
                self.verbose = True
            else:
                self.ShowUsage()
                if o == "-h":
                    return 0
                return 1
        if not self.identity_file:
            self.ShowUsage()
            return 1

        if self.verbose:
            print("Using identity_file: %s" % self.identity_file)
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
            with open(filename, 'rb') as f:
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
            with open(filename, 'wb') as content_file:
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
        priv = self.Read(self.private_file, "private key")
        print(priv)
        if priv != None:
            self.private_key = RSA.importKey(priv)

        # read public key
        self.public_key = self.Read(self.public_file, "public key")

        if self.private_key and self.public_key:
            return True
        return False

    def Create(self):
        #http://stackoverflow.com/a/22449476
        key = RSA.generate(1024, os.urandom)
        self.private_key = key
        self.Write(self.private_file, key.exportKey('PEM'), "private key")
        os.chmod(self.private_file, 0o755)
        pubkey = key.publickey()
        self.public_key = pubkey.exportKey()
        self.Write(self.public_file, self.public_key, "public key")

    def GetPrivateKey(self):
        return self.private_key.n, self.private_key.e, self.private_key.d

    def GetPublicKey(self):
        return self.public_key

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
