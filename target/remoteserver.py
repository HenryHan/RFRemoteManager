from robotremoteserver import RobotRemoteServer
from robotremoteserver import StandardStreamInterceptor
from robotremoteserver import KeywordResult
from robotremoteserver import BINARY
import os,sys
import importlib
cur_dir = os.path.dirname(os.path.abspath(__file__))

class RemoteServer(RobotRemoteServer):

    def __init__(self, host='127.0.0.1', port=8270, port_file=None,
                 allow_stop='DEPRECATED', serve=True, allow_remote_stop=True):
        RobotRemoteServer.__init__(self,os, host,port,port_file,allow_stop,serve,allow_remote_stop)
        self.library_list = []

    def _register_functions(self, server):
        server.register_function(self.run_script)
        server.register_function(self.save_file)
        server.register_function(self.reload_library_list)
        RobotRemoteServer._register_functions(self, server)

    def run_script(self, script):
        sr = ScriptRunner(script)
        return sr.run_script()

    def reload_library_list(self,reload_scripts,library_list_str):
        exec(reload_scripts)
        exec("self.library_list = "+library_list_str)
        print(self.library_list)
        return True

    def save_file(self, target_file, binary_data):
        full_path = cur_dir+"\\"+target_file
        target_dir = os.path.dirname(full_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(full_path, "wb") as handle:
            handle.write(binary_data.data)
            handle.close()
        return True

class ScriptRunner():
    def __init__(self, script):
        self._script = script

    def run_script(self):
        result = KeywordResult()
        with StandardStreamInterceptor() as interceptor:
            try:
                return_value = exec(self._script)
            except Exception:
                result.set_error(*sys.exc_info())
            else:
                try:
                    result.set_return(return_value)
                except Exception:
                    result.set_error(*sys.exc_info()[:2])
                else:
                    result.set_status('PASS')
        result.set_output(interceptor.output)
        print(self._script)
        print(result.data)
        return result.data

if __name__ == "__main__":
    rs = RemoteServer()