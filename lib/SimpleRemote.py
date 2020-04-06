from robot.libraries.Remote import Remote
from robot.libraries.Remote import XmlRpcRemoteClient
from robot.utils import timestr_to_secs
from robot.errors import RobotError
from robot.libraries.BuiltIn import BuiltIn
import socket
import os
import json
try:
    import xmlrpclib
except ImportError:  # Py3
    import xmlrpc.client as xmlrpclib
try:
    from xml.parsers.expat import ExpatError
except ImportError:
    class ExpatError(Exception):
        pass


class SimpleRemote(Remote):

    def __init__(self, lab, timeout=None):
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.get_env_file()
        self.get_lab_ip_port(lab)
        BuiltIn().log_to_console("**connecting to %s:%s" % (self.ip,self.port))
        uri = 'http://%s:%s' % (self.ip,self.port)
        if timeout:
            timeout = timestr_to_secs(timeout)
        self._uri = uri
        self._client = SimpleClient(uri, timeout)
        self.transfer_and_import_library()
    
    def transfer_and_import_library(self):
        self._transfer_list = [
            "\\RemoteLibrary\\RemoteLibrary.py",
            "\\RemoteLibrary\\RemoteLibrary2.py"
        ]
        for file in self._transfer_list:
            self.transfer_file(self.cur_dir+file,os.path.basename(file))
        reload_scripts = "import RemoteLibrary\n"
        reload_scripts += "importlib.reload(RemoteLibrary)\n"
        reload_scripts += "import RemoteLibrary2\n"
        reload_scripts += "importlib.reload(RemoteLibrary2)\n"
        reload_scripts += "tc= RemoteLibrary2.TestClass()\n"
        library_list_str = "[tc,RemoteLibrary]"
        self.reload_library_list(reload_scripts,library_list_str)
    
    def get_env_file(self):
        self.env_file =  self.cur_dir+"\\env.json"

    def get_lab_ip_port(self, lab):
        self.ip = None
        self.port = None
        file = open(self.env_file,encoding="utf-8")
        env = json.load(file)
        for item in env:
            if lab in item.keys():
                lab = item[lab]
        for item in env:
            if "name" in item.keys():
                if item["name"] == lab:
                    self.ip = item["ip"]
                    self.port = item["port"]
        if self.ip and self.port:
            return True
        else:
            raise RobotError("get ip or port failed!")

    def transfer_file(self, local_file, target_file):
        return self._client.transfer_file(local_file, target_file)

    def reload_library_list(self,reload_scripts,library_list_str):
        return self._client.reload_library_list(reload_scripts,library_list_str)

class SimpleClient(XmlRpcRemoteClient):

    def transfer_file(self, local_file, target_file):
            with open(local_file, "rb") as handle:
                binary_data = xmlrpclib.Binary(handle.read())
            return self._server.save_file(target_file, binary_data)

    def reload_library_list(self,reload_scripts,library_list_str):
        return self._server.reload_library_list(reload_scripts,library_list_str)

    def run_keyword(self, name, args, kwargs):
        env = {}
        env["suite_name"] = str(BuiltIn().get_variable_value("${SUITE NAME}"))
        env["test_name"] = str(BuiltIn().get_variable_value("${TEST NAME}"))
        env["test_tags"] = str(BuiltIn().get_variable_value("${TEST TAGS}"))
        run_keyword_args = [name, args, env, kwargs] if kwargs else [name, args, env]
        try:
            result = self._server.run_keyword(*run_keyword_args)
            if "error" in result.keys():
                result["error"] = result["error"] + "\n==============traceback=============\n" + result["traceback"]
            return result
        except xmlrpclib.Fault as err:
            message = err.faultString
        except socket.error as err:
            message = 'Connection to remote server broken: %s' % err
        except ExpatError as err:
            message = ('Processing XML-RPC return value failed. '
                       'Most often this happens when the return value '
                       'contains characters that are not valid in XML. '
                       'Original error was: ExpatError: %s' % err)
        raise RuntimeError(message)

if __name__=="__main__":
    sr = SimpleRemote("target_1")