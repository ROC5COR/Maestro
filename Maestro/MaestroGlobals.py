
import threading

server_list_lock = threading.RLock() # Lock to ensure multithreading access
SERVER_LIST = []

scenario_list_lock = threading.RLock()
SCENARIO_LIST = []
