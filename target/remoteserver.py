from robotremoteserver import RobotRemoteServer
from robotremoteserver import StandardStreamInterceptor
from robotremoteserver import KeywordResult
from robotremoteserver import BINARY
from robotremoteserver import RemoteLibraryFactory
from robotremoteserver import KeywordRunner
import os,sys
import importlib
cur_dir = os.path.dirname(os.path.abspath(__file__))

class RemoteServer(RobotRemoteServer):

    def __init__(self, host='0.0.0.0', port=8270, port_file=None,
                 allow_stop='DEPRECATED', serve=True, allow_remote_stop=True):
        RobotRemoteServer.__init__(self,os, host,port,port_file,allow_stop,serve,allow_remote_stop)
        self.library_list = []
        self.library_keywords = {}

    def _register_functions(self, server):
        server.register_function(self.save_file)
        server.register_function(self.reload_library_list)
        RobotRemoteServer._register_functions(self, server)

    def reload_library_list(self,reload_scripts,library_list_str):
        exec(reload_scripts)
        exec("self.library_list = "+library_list_str)
        for module in self.library_list:
            _library = RemoteLibraryFactory(module)
        self.get_keyword_names()
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

    def get_keyword_names(self):
        self.library_keywords = {}
        key_words = []
        for library in self.library_list:
            instance = RemoteLibraryFactory(library)
            self.library_keywords[instance] = instance.get_keyword_names()
            key_words+=self.library_keywords[instance]
        return key_words + ['stop_remote_server']

    def run_keyword(self, name, args, kwargs=None):
        if name == 'stop_remote_server':
            return KeywordRunner(self.stop_remote_server).run_keyword(args, kwargs)
        for instance in self.library_keywords.keys():
            if name in self.library_keywords[instance]:
                return instance.run_keyword(name, args, kwargs)
        raise "Keyword not found" 

    def get_keyword_arguments(self, name):
        if name == 'stop_remote_server':
            return []
        for instance in self.library_keywords.keys():
            if name in self.library_keywords[instance]:
                return instance.get_keyword_arguments(name)
        return []
    
    def get_keyword_documentation(self, name):
        if name == 'stop_remote_server':
            return ('Stop the remote server unless stopping is disabled.\n\n'
                    'Return ``True/False`` depending was server stopped or not.')
        for instance in self.library_keywords.keys():
            if name in self.library_keywords[instance]:
                return instance.get_keyword_documentation(name)
        return ""

    def get_keyword_tags(self, name):
        if name == 'stop_remote_server':
            return []
        for instance in self.library_keywords.keys():
            if name in self.library_keywords[instance]:
                return instance.get_keyword_tags(name)
        return []

if __name__ == "__main__":
    rs = RemoteServer()