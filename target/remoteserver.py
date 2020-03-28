from robotremoteserver import RobotRemoteServer
import os

class RemoteServer(RobotRemoteServer):
    def _register_functions(self, server):
        server.register_function(self.run_script)
        RobotRemoteServer._register_functions(self, server)

    def run_script(self, script):
        print(script)

if __name__ == "__main__":
    lib = os
    rs = RemoteServer(os, serve=False)
    rs.serve()