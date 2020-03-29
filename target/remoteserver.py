from robotremoteserver import RobotRemoteServer
from robotremoteserver import StandardStreamInterceptor
from robotremoteserver import KeywordResult
from robotremoteserver import BINARY
import os,sys
cur_dir = os.path.dirname(os.path.abspath(__file__))

class RemoteServer(RobotRemoteServer):
    def _register_functions(self, server):
        server.register_function(self.run_script)
        server.register_function(self.save_file)
        RobotRemoteServer._register_functions(self, server)

    def run_script(self, script):
        sr = ScriptRunner(script)
        print(script)
        return sr.run_script()

    def save_file(self, target_file, binary_data):
        target_dir = os.path.dirname(cur_dir+target_file)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(cur_dir+target_file, "wb") as handle:
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
    lib = os
    rs = RemoteServer(os)