from robot.libraries.Remote import Remote
from robot.libraries.Remote import XmlRpcRemoteClient
from robot.utils import timestr_to_secs
try:
    import xmlrpclib
except ImportError:  # Py3
    import xmlrpc.client as xmlrpclib

class SimpleRemote(Remote):

    def __init__(self, uri='http://127.0.0.1:8270', timeout=None):
        if '://' not in uri:
            uri = 'http://' + uri
        if timeout:
            timeout = timestr_to_secs(timeout)
        self._uri = uri
        self._client = SimpleClient(uri, timeout)

    def run_script(self, script):
        return self._client.run_script(script)

    def transfer_file(self, local_file, target_file):
        return self._client.transfer_file(local_file, target_file)

class SimpleClient(XmlRpcRemoteClient):

    def run_script(self, script):
        return self._server.run_script(script)

    def transfer_file(self, local_file, target_file):
            with open(local_file, "rb") as handle:
                binary_data = xmlrpclib.Binary(handle.read())
            return self._server.save_file(target_file, binary_data)

if __name__=="__main__":
    sr = SimpleRemote()
    script = '''
import os
print(os.path.exists("D:\\test\\1.txt"))
    '''
    import re
    print(sr.run_script(re.escape(script)))