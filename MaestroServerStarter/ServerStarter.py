import json
import os
import threading
from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerDiscoveryProtocolClient
from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerInformationMessage



class ServerStarter:
    def __init__(self, config_file):
        self.config = dict()
        self.server_configs = []
        self.server_classes = []
        self._base_dir = os.path.dirname(__file__)

        self.load_config(config_file)
        if self.update:
            self.download_dependencies()

        self.get_server_configs()
        self.load_server_configs()
        self.configure_env()
        self.start_servers()

    
    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
                f.close()
        except:
            pass
        
        self.server_storage_dir = self.config.get('server_storage_dir', os.path.join(self._base_dir,'server_storage'))
        self.dependencies = self.config.get('dependencies', [])
        self.update = self.config.get('update', False)
        self.daemon_listen_port = self.config.get('daemon_listen_port', 7878)
        self.server_start_port = self.config.get('server_start_port', 8001)
        self.envs = self.config.get('envs', {})

        with open(config_file, 'w') as f:
            json.dump({
                'server_storage_dir':self.server_storage_dir,
                'dependencies': self.dependencies,
                'update':self.update,
                'daemon_listen_port':self.daemon_listen_port,
                'server_start_port': self.server_start_port,
                'envs':self.envs
            }, f, indent=4, sort_keys=True)
            f.close()

    def download_dependencies(self):
        import requests
        from urllib.parse import urlparse
        import zipfile

        if not os.path.exists(self.server_storage_dir):
            os.makedirs(self.server_storage_dir)

        for dep in self.dependencies:
            print("Downloading: {}".format(dep))
            r = requests.get(dep)
            storage_name = urlparse(dep).path.replace('/','.')
            storage_path = os.path.join(self.server_storage_dir,storage_name)

            with open(storage_path,'wb') as f:
                f.write(r.content)
                f.close()

            print("Extracting: {} to: {}".format(storage_name, self.server_storage_dir))
            with zipfile.ZipFile(storage_path, 'r') as z:
                z.extractall(self.server_storage_dir)
            
    def get_server_configs(self):
        for _, dirs, _ in os.walk(self.server_storage_dir):
            for dir in dirs:
                server_main_dir = os.path.join(self.server_storage_dir, dir)
                file_path = os.path.join(server_main_dir, 'maestro_server.json')
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        server_conf = json.load(f)
                        self.server_configs.append((server_main_dir, server_conf))
    
    def load_server_configs(self):
        from importlib import import_module

        for server_config in self.server_configs:
            if 'entryfile' not in server_config[1]:
                print("Missing 'entryfile' in server config file at {}".format(server_config[0]))
                continue

            if 'entryclass' not in server_config[1]:
                print("Missing 'entryclass' in server config file at {}".format(server_config[0]))
                continue

            if 'version' not in server_config[1]:
                print("Missing 'version' in server config file at {}".format(server_config[0]))
                continue

            
            entryfile = server_config[1]['entryfile']
            entryclass = server_config[1]['entryclass']
            version = server_config[1]['version']

            modulepath = server_config[0].replace('/','.') + "." + entryfile[:-3] if entryfile.endswith('.py') else entryfile
            #modulepath = '.'.join(modulepath.split('.')[1:]) # Removing first module level
            print("Loading: {}".format(modulepath))
            #print(server_config[0], entryfile, entryclass)
            try:
                imported_module = import_module(modulepath)
                module_class = getattr(imported_module, entryclass)
                if issubclass(module_class, threading.Thread):
                    self.server_classes.append((module_class, version, entryclass))
                else:
                    print("Error: trying to load a class that is not a subclass of Thread")
                    continue
            except Exception as e:
                print("Failed to load module: {}".format(e))
                continue

    def configure_env(self):
        for k,v in self.envs.items():
            os.environ[k] = v
        

    def start_servers(self):
        current_port = self.server_start_port
        for server_class, server_version, server_name in self.server_classes:
            print("Starting server: {} on port {}".format(server_name, current_port))
            inst = server_class(current_port)
            inst.start() #TODO: Start SDP Daemon before that

            sdp_client = ServerDiscoveryProtocolClient(self.daemon_listen_port)
            sdp_client.set_message(ServerInformationMessage(server_name, current_port, server_version))
            sdp_client.start()

            current_port += 1


            





if __name__ == '__main__':
    firestarter = ServerStarter('server_starter.json')


