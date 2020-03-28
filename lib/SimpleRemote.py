from robot.libraries.Remote import Remote
from robot.libraries.Remote import XmlRpcRemoteClient
from robot.utils import timestr_to_secs

class SimpleRemote(Remote):

    def __init__(self, uri='http://127.0.0.1:8270', timeout=None):
        if '://' not in uri:
            uri = 'http://' + uri
        if timeout:
            timeout = timestr_to_secs(timeout)
        self._uri = uri
        self._client = SimpleClient(uri, timeout)

    def run_script(self, script):
        self._client.run_script(script)

class SimpleClient(XmlRpcRemoteClient):

    def run_script(self, script):
        self._server.run_script(script)

if __name__=="__main__":
    sr = SimpleRemote()
    sr.run_script("import os")

