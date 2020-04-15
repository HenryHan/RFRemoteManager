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

    def __init__(self, ip="127.0.0.1", port=8270, timeout=None):
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
        BuiltIn().log_to_console("**connecting to %s:%s" % (ip,port))
        uri = 'http://%s:%s' % (ip,port)
        if timeout:
            timeout = timestr_to_secs(timeout)
        self._uri = uri
        self._client = SimpleClient(uri, timeout)
        try:
            self.transfer_and_import_library()
        except:
            pass
    
    def transfer_and_import_library(self):
        self._transfer_list = [
            "\\RemoteLibrary\\RemoteLibrary.py",
            "\\RemoteLibrary\\RemoteLibrary2.py"
        ]
        for file in self._transfer_list:
            self.transfer_file(self.cur_dir+file,os.path.basename(file))
        self.reload_scripts = "import RemoteLibrary\n"
        self.reload_scripts += "importlib.reload(RemoteLibrary)\n"
        self.reload_scripts += "import RemoteLibrary2\n"
        self.reload_scripts += "importlib.reload(RemoteLibrary2)\n"
        self.reload_scripts += "tc= RemoteLibrary2.TestClass()\n"
        self.reload_scripts += "self.library_list=[tc,RemoteLibrary]"
        self.reload_library_list(self.reload_scripts)

    def transfer_file(self, local_file, target_file):
        return self._client.transfer_file(local_file, target_file)

    def reload_library_list(self,reload_scripts):
        return self._client.reload_library_list(reload_scripts)

class SimpleClient(XmlRpcRemoteClient):

    def transfer_file(self, local_file, target_file):
            with open(local_file, "rb") as handle:
                binary_data = xmlrpclib.Binary(handle.read())
            return self._server.save_file(target_file, binary_data)

    def reload_library_list(self,reload_scripts):
        return self._server.reload_library_list(reload_scripts)

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
    sr = SimpleRemote("10.91.44.162")