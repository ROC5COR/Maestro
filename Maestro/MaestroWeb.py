import threading
import json
from Maestro.MaestroGlobals import SCENARIO_LIST, scenario_list_lock, SERVER_LIST, server_list_lock
from wsgiref import simple_server
import falcon
import os


class MaestroWebRoutes:
    class ServerList:
        def on_get(self, req, res):
            res.content_type = 'application/json'
            with server_list_lock:
                res.body = json.dumps(SERVER_LIST)
    
    class ApplicationList:
        def on_get(self, req, res):
            res.content_type = 'application/json'
            with scenario_list_lock:
                data = []
                for scenario in SCENARIO_LIST:
                    data.append({
                        'name':scenario.name,
                        'status':scenario.status,
                        'uuid':str(scenario.uuid)
                    })
                res.body = json.dumps(data)

    class ApplicationOutputVariables:
        def on_get(self, req, res, **kwargs):
            with scenario_list_lock:
                for scenario in SCENARIO_LIST:
                    if str(scenario.uuid) == kwargs.get('uuid'):
                        res.content_type = 'application/json' # Depends on the variables
                        res.body = json.dumps(scenario.output_variables)
                        return
            res.body = json.dumps({})

    class ApplicationName:
        def on_get(self, req, res, **kwargs):
            res.content_type = 'text/plain'
            with scenario_list_lock:
                for scenario in SCENARIO_LIST:
                    if str(scenario.uuid) == kwargs.get('uuid'):
                        res.body = scenario.name
                        return
            res.body = "ERROR"

class MaestroWebServer(threading.Thread):
    def __init__(self, exposed_port):
        threading.Thread.__init__(self)
        api = falcon.API()
        static_files_dir = os.path.abspath('./Maestro/web_static_files')
        print("[MaestroWebServer] Static files dir: ",static_files_dir)
        api.add_static_route('/', static_files_dir)
        api.add_route('/server_list', MaestroWebRoutes.ServerList())
        api.add_route('/application_list', MaestroWebRoutes.ApplicationList())
        api.add_route('/applications', MaestroWebRoutes.ApplicationList())
        api.add_route('/applications/{uuid}/name', MaestroWebRoutes.ApplicationName())
        api.add_route('/applications/{uuid}/variables', MaestroWebRoutes.ApplicationOutputVariables())
        self.server = simple_server.make_server('', exposed_port, app=api)

    def run(self):
        print("[MaestroWebServer] Starting server")
        self.server.serve_forever()