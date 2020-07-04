import threading
from Maestro.MaestroGlobals import SCENARIO_LIST, scenario_list_lock, SERVER_LIST, server_list_lock
import uuid
import time

class MaestroScenarioV2:
    """
    This class need to be overriden, otherwise does nothing ^^
    """
    def __init__(self, name):
        # scenario_runner: to access "high level commands"
        self.uuid = uuid.uuid4()
        self.status = "Stopped"
        self.name = name
        self.scenario_runner = None # If None the scenario can't call helpers
        self.dependencies = [] # List of server dependencies
        self.output_variables = dict() # Needed to output variables through UIs
        print("[ScenarioV2:INFO] Starting scenario ",self.name)

    def run(self):
        print("[ScenarioV2:INFO] Empty scenario running")
        pass # To override

    def set_scenario_runner(self, runner):
        self.scenario_runner = runner

    def get_dependencies(self):
        return self.dependencies

class MaestroScenarioRunnerV2(threading.Thread):
    def __init__(self, scenario):
        threading.Thread.__init__(self)
        self.scenario = scenario
        self.running = True


    def run(self):
        if self.scenario is not None:
            while not self.are_dependencies_ok():
                self.scenario.status = "Waiting dependencies"
                time.sleep(4)

            try:
                self.scenario.status = "Running"
                self.scenario.run() # This is not a thread
            except Exception as e:
                print("[ScenarioRunner2:ERROR] Exception occured while running scenario (",self.scenario.name,"):",e)
                self.scenario.status = "Error: stopped"
            finally:
                self.running = False
                print("[ScenarioRunnerV2:INFO] Scenario ",self.scenario.name, " has ended")
                self.scenario.status = "Ended"


    ### Helpers ###
    def are_dependencies_ok(self):
        if self.scenario is not None and self.scenario.get_dependencies() is not None:
            for dependency in self.scenario.get_dependencies():
                if isinstance(dependency, str):
                    with server_list_lock:
                        dep_solved = False
                        for server_info in SERVER_LIST:
                            if server_info['name'] == dependency:
                                dep_solved = True
                                break
                        if not dep_solved:
                            return False
                else:
                    print("[MSR:TODO] Not str dependencies are not managed")
            return True
        else:
            return True
        
