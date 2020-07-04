from Maestro.MaestroGlobals import SCENARIO_LIST, scenario_list_lock, SERVER_LIST, server_list_lock
import requests

def make_get(from_server, at_url):
        with server_list_lock:
            for server_info in SERVER_LIST:
                if server_info['name'] == from_server:
                    addr = 'http://' + str(server_info['source'])+':'+str(server_info['port'])+str(at_url)
                    try:
                        r = requests.get(addr)
                        if r.status_code == 200:
                            return r.content
                        else:
                            return None
                    except requests.ConnectionError as e:
                        print("[ERROR] Error while GETting connecting to ",addr,": ",e)
                        return None
                    
        
def make_post(from_server, at_url, post_params, post_data):
    with server_list_lock:
        for server_info in SERVER_LIST:
            if server_info['name'] == from_server:
                try:
                    addr = 'http://' + str(server_info['source'])+':'+str(server_info['port'])+str(at_url)
                    r = requests.post(addr, params=post_params, data=post_data)
                    if r.status_code == 200:
                        if r.headers['content-type'] == 'application/json':
                            return r.json()
                        else:
                            return r.content
                    else:
                        print("[ERROR] POST request return non 200 code: ",r.status_code)
                        return None
                except requests.ConnectionError as e:
                    print("[ERROR] POST error: ",e)
                    return None
                