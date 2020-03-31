from robot.libraries.Remote import Remote
from robot.libraries.Remote import XmlRpcRemoteClient
from robot.utils import timestr_to_secs
from imp import reload
import os
import json
try:
    import xmlrpclib
except ImportError:  # Py3
    import xmlrpc.client as xmlrpclib


class SimpleRemote(Remote):

    def __init__(self, lab, timeout=None):
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.get_env_file()
        self.get_lab_ip_port(lab)
        uri = 'http://%s:%s' % (self.ip,self.port)
        if timeout:
            timeout = timestr_to_secs(timeout)
        self._uri = uri
        self._client = SimpleClient(uri, timeout)
        self.transfer_and_import_library()
    
    def transfer_and_import_library(self):
        self._transfer_list = [
            "\\RemoteLibrary\\mylib.py",
            "\\RemoteLibrary\\RemoteLibrary.py"
        ]
        for file in self._transfer_list:
            self.transfer_file(self.cur_dir+file,os.path.basename(file))
        reload_scripts = "import mylib\n"
        reload_scripts += "importlib.reload(mylib)\n"
        reload_scripts += "import RemoteLibrary\n"
        reload_scripts += "importlib.reload(RemoteLibrary)"
        library_list_str = "[mylib,RemoteLibrary]"
        self.reload_library_list(reload_scripts,library_list_str)
    
    def get_env_file(self):
        self.env_file =  self.cur_dir+"\\env.json"

    def get_lab_ip_port(self, lab):
        self.ip = "127.0.0.1"
        self.port = 8270
        if os.path.exists(self.env_file):
            file = open(self.env_file,encoding="utf-8")
            env = json.load(file)
            if lab in env.keys():
                if env[lab] is dict:
                    self.ip = env[lab]["ip"]
                    self.port = env[lab]["port"]
                else:
                    self.ip = env[env[lab]]["ip"]
                    self.port = env[env[lab]]["port"]


    def run_script(self, script):
        return self._client.run_script(script)

    def transfer_file(self, local_file, target_file):
        return self._client.transfer_file(local_file, target_file)

    def reload_library_list(self,reload_scripts,library_list_str):
        return self._client.reload_library_list(reload_scripts,library_list_str)

class SimpleClient(XmlRpcRemoteClient):

    def run_script(self, script):
        return self._server.run_script(script)

    def transfer_file(self, local_file, target_file):
            with open(local_file, "rb") as handle:
                binary_data = xmlrpclib.Binary(handle.read())
            return self._server.save_file(target_file, binary_data)

    def reload_library_list(self,reload_scripts,library_list_str):
        return self._server.reload_library_list(reload_scripts,library_list_str)

if __name__=="__main__":
    sr = SimpleRemote("target_1")
    sr.get_keyword_names()