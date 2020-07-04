import threading
from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerDiscoveryProtocolListener
from ServerDiscoveryProtocol.ServerDiscoveryProtocol import BROADCAST_PORT
from Maestro.MaestroScenarioV2 import MaestroScenarioRunnerV2, MaestroScenarioV2
from Maestro.MaestroGlobals import SCENARIO_LIST, scenario_list_lock, SERVER_LIST, server_list_lock
from Maestro.MaestroWeb import MaestroWebServer
import falcon
from wsgiref import simple_server
import json
import os
import time
import requests
import uuid


class MaestroTimeWatcher(threading.Thread):
    def __init__(self, check_every=2):
        threading.Thread.__init__(self)
        self.check_every = check_every
    def run(self):
        while True:
            with server_list_lock:
                i = 0
                while i < len(SERVER_LIST):
                    if (time.time() - SERVER_LIST[i]['updated_at']) > 30:
                        SERVER_LIST.remove(SERVER_LIST[i])
                    else:
                        i += 1
            time.sleep(self.check_every)




class Maestro(threading.Thread):
    def __init__(self, exposed_port, show_debug=False):
        threading.Thread.__init__(self)
        self.show_debug = show_debug
        self.sdp_listener = ServerDiscoveryProtocolListener(BROADCAST_PORT, show_info=False, show_debug=False)
        self.sdp_listener.set_callback_on_received_message(self.server_list_updated)
        self.exposed_port = exposed_port
        self.web_server = MaestroWebServer(exposed_port=exposed_port)
        self.mtw = MaestroTimeWatcher(check_every=2)

        # from Maestro.apps.SricamFaceDetect.SricamFaceDetect import SricamFaceDetect
        # SCENARIO_LIST.append(SricamFaceDetect())

        # from Maestro.apps.SricamFaceSpeaker.SricamFaceSpeaker import SricamFaceSpeaker
        # SCENARIO_LIST.append(SricamFaceSpeaker())

        from Maestro.apps.SricamFaceReco.SricamFaceReco import SricamFaceRecognition
        SCENARIO_LIST.append(SricamFaceRecognition())


        self.scenario_runners = []
        for scenario in SCENARIO_LIST:
            if isinstance(scenario, MaestroScenarioV2):
                msr = MaestroScenarioRunnerV2(scenario)
                scenario.set_scenario_runner(msr)
                self.scenario_runners.append(msr)


        
    def server_list_updated(self):
        server_dict = self.sdp_listener.get_servers()
        with server_list_lock:
            SERVER_LIST.clear()
            for k in server_dict.keys():
                SERVER_LIST.append(server_dict[k])
                if self.show_debug:
                    print("[Maestro:DEBUG] Server list: ", server_dict[k])

    def run(self):
        print("[INFO:Maestro] Starting Maestro on port:",self.exposed_port)
        self.sdp_listener.start()
        self.web_server.start()
        self.mtw.start()
        for scenario in self.scenario_runners:
            scenario.start()

        self.sdp_listener.join()
        self.web_server.join()
        self.mtw.join()
        for scenario in self.scenario_runners:
            scenario.join()
        
