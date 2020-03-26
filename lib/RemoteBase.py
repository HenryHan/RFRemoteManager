#encoding=utf-8
from robot.libraries.Remote import Remote
from robot.libraries.Remote import XmlRpcRemoteClient
from robot.utils import timestr_to_secs
import os.path
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import inspect
import Helper
import socket
from robot.libraries.BuiltIn import BuiltIn
try:
    from xml.parsers.expat import ExpatError
except ImportError:
    class ExpatError(Exception):
        pass

try:
    import xmlrpclib
except ImportError:  # Py3
    import xmlrpc.client as xmlrpclib


class RemoteBase(Remote):
    _libpath = ""
    library = None
    robot_name_index = {}

    def __init__(self, uri='http://127.0.0.1:8270', timeout=None):
        if '://' not in uri:
            uri = 'http://' + uri
        if timeout:
            timeout = timestr_to_secs(timeout)
        self._uri = uri
        ip, port = uri.split("//")[1].split(":")
        if not Helper.test_remote_port(ip, port, 3, 1):
            assert False, "连接Agent出错"
        self._client = FcBaseClient(uri, timeout)
        if self._libpath:
            my_path = os.path.abspath(os.path.dirname(__file__))
            libpath=os.path.join(my_path, self._libpath)
            try:
                self.send_remotelib(libpath)
            except Exception:
                pass

    def get_keyword_names(self):
        names = []
        for name, kw in inspect.getmembers(self.library):
                if getattr(kw, 'robot_name', None):
                    names.append(kw.robot_name)
                    self.robot_name_index[kw.robot_name] = name
                elif name[0] != '_' and inspect.ismethod(kw):
                    names.append(name)
        return names

    def get_keyword_arguments(self, name):
        if __name__ == '__init__':
            return []
        if name in self.robot_name_index:
            name = self.robot_name_index[name]
        kw = getattr(self.library, name)
        args, varargs, kwargs, defaults = inspect.getargspec(kw)
        if inspect.ismethod(kw):
            args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += ['%s=%s' % (n, d) for n, d in zip(names, defaults)]
        if varargs:
            args.append('*%s' % varargs)
        if kwargs:
            args.append('**%s' % kwargs)
        return args

    def get_keyword_documentation(self, name):
        if name in self.robot_name_index:
            name = self.robot_name_index[name]
        kw = getattr(self.library, name)
        return inspect.getdoc(kw) or ''

    def get_keyword_tags(self, name):
        if name in self.robot_name_index:
            name = self.robot_name_index[name]
        kw = getattr(self.library, name)
        return getattr(kw, 'robot_tags', [])

    def send_remotelib(self,libpath):
        self._client.send_remotelib(libpath)

    def receive_file(self,source,target):
        self._client.receive_file(source,target)


class FcBaseClient(XmlRpcRemoteClient):

    def send_remotelib(self, libpath):
            with open(libpath, "rb") as handle:
                binary_data = xmlrpclib.Binary(handle.read())
            return self._server.receive_remotelib(binary_data)

    def receive_file(self,source,target):
        with open(target, "wb") as handle:
            handle.write(self._server.send_file(source).data)
            handle.close()

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

