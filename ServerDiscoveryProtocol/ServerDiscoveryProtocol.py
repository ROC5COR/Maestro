from socket import *
import threading
import time
import json

BROADCAST_PORT = 16761

class MessageBroadcaster:
    def __init__(self, broadcast_addr, broadcast_port):
        self.broadcast_addr = broadcast_addr
        self.port = broadcast_port
        
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
          
    def broadcast(self, data):
        if isinstance(data, str):
            data = data.encode('utf8')

        if not isinstance(data, bytes):
            print("[MessageBroadcaster:ERROR] Message to broadcast must be bytes not: ",type(data))
            return
        self.socket.sendto(data, (self.broadcast_addr, self.port))



class ServerDiscoveryProtocolDaemon(threading.Thread):
    def __init__(self, broadcast_addr, broadcast_port, listen_port):
        threading.Thread.__init__(self)
        self.listen_port = listen_port
        self.mb = MessageBroadcaster(broadcast_addr, broadcast_port)

        self.socket = socket(AF_INET, SOCK_STREAM)

    def run(self):
        try:
            self.socket.bind(('127.0.0.1', self.listen_port))
        except Exception as e:
            print("[SDPDaemon:ERROR] while starting daemon. ",e)
            self.socket.close()
            raise

        self.socket.listen(1)

        print("[SDPDaemon:INFO] Daemon started")
        while True:
            # Wait for a connection
            #print("[SDPDaemon:INFO] Daemon waiting for a connection")
            connection, client_address = self.socket.accept()
            try:
                while True:
                    data = connection.recv(1024)
                    if data:
                        print("[SDPDaemon:DEBUG] Data received from client (",client_address,"):",data)
                        connection.sendall(b"ok")
                        self.mb.broadcast(data)
                    else:
                        break
                    
            finally:
                connection.close()
        
        

class MessageListener(threading.Thread):
    def __init__(self, listen_port, show_info=False, show_debug=False):
        threading.Thread.__init__(self)
        self.listen_port = listen_port
        self.callback = None
        self.show_info = show_info
        self.show_debug = show_debug

        self.socket = socket(AF_INET, SOCK_DGRAM)

    def set_callback(self, callback):
        self.callback = callback

    def run(self):
        try:
            self.socket.bind(('', self.listen_port))
        except:
            print("[MessageListener:ERROR] Failed to bind to port ", self.listen_port)
            self.socket.close()
            raise
        
        if self.show_info:
            print("[MessageListener:INFO] MessageListener server started")
        while True:
            data, addr = self.socket.recvfrom(1024) # <-- waiting forever
            if self.show_debug:
                print("[MessageListener:DEBUG] Addr:",addr)
            try:
                if self.callback is not None:
                    self.callback(json.loads(data.decode('utf8')), addr)
                    if self.show_debug:
                        print('[MessageListener:DEBUG] JSON:', json.loads(data.decode('utf8')))
            except json.JSONDecodeError as e:
                if self.show_debug:
                    print('[MessageListener:DEBUG] Raw:', data,'(',e,')')

    def stop_listening(self):
        self.socket.close()

class ServerDiscoveryProtocolListener(threading.Thread):
    def __init__(self, listen_port, show_info=False, show_debug=False):
        threading.Thread.__init__(self)
        self.show_info = show_info
        self.show_debug = show_debug

        self.ml = MessageListener(listen_port, show_info=show_info, show_debug=show_debug)
        self.ml.set_callback(self.message_received)
        self.server_information = dict()
        self.callback_on_received_message = None

    def message_received(self, message, connection):
        if 'version' in message and 'server' in message:
            if self.show_debug:
                print("[SDPListener:DEBUG] Message received: ",message, connection)
            server = message['server']
            source_addr = connection[0]
            server['source'] = source_addr
            server['updated_at'] = time.time()
            if 'name' in server and 'port' in server and 'version' in server:
                concat = str(server['name']) + str(server['source']) + str(server['port']) + str(server['version'])
                self.server_information[concat] = server
                if self.callback_on_received_message is not None:
                    self.callback_on_received_message()

                if self.show_debug:
                    print("[SDPListener:DEBUG] Current dict: ",self.server_information)
        else:
            print("[SDPListener:WARNING] Message received without version or server field")

    def set_callback_on_received_message(self, callback):
        # Callback taking no parameter
        self.callback_on_received_message = callback
    
    def get_servers(self):
        return self.server_information

    def run(self):
        self.ml.start()
        self.ml.join()

class ServerDiscoveryProtocolClient(threading.Thread):
    def __init__(self, daemon_port, message_interval=15, show_info=False, show_debug=False):
        threading.Thread.__init__(self)
        self.port = daemon_port
        self.message_interval = message_interval
        self.show_info = show_info
        self.show_debug = show_debug
        self.socket = None
        self.data = None

    def set_message(self, data):
        if isinstance(data, str):    
            self.data = data
        elif isinstance(data, ServerInformationMessage):
            self.data = data.json()
        else:
            print("[SDPClient:ERROR] Can't set data of type:",type(data))
            self.data = None

    def run(self):
        while True:
            try:
                if self.data is None:
                    continue
                self.socket = create_connection(('localhost', self.port))
                self.socket.sendall(self.data.encode('utf8'))
                
                response = self.socket.recv(16)
                if len(response) == 2:
                    if response != b'ok':
                        print("[SDPClient:ERROR] Error daemon doesn't reply OK")
                    else:
                        if self.show_info:
                            print("[SDPClient:INFO] Message sent to the daemon")
            except ConnectionRefusedError as e:
                print("[SDPClient:ERROR] Daemon does not seems to be started on port")
            except Exception as e:
                print("[SDPClient:ERROR] Error: ",e)
            finally:
                if self.socket is not None:
                    if self.show_info:
                        print("[SDPClient:INFO] Disconnecting from daemon")
                    self.socket.close()
            time.sleep(self.message_interval)

import json
class ServerInformationMessage:

    MESSAGE_VERSION = '0.1'
    
    def __init__(self, server_name, server_listen_port, server_version):
        self.server_name = server_name
        self.server_listen_port = server_listen_port
        self.server_version = server_version

    def json(self):
        return json.dumps({
            'version':self.MESSAGE_VERSION,
            'server':{
                'name':self.server_name,
                'port':self.server_listen_port,
                'version':self.server_version
            }
        })


if __name__ == '__main__':
    print("Start")
    ml = MessageListener(6767)
    ml.start()

    daemon = ServerDiscoveryProtocolDaemon("192.168.0.255", 6767, 8000)
    daemon.start()

    client_progam = ServerDiscoveryProtocolClient(8000)
    client_progam.set_message(json.dumps({'key1':'value1'}))
    client_progam.start()

    time.sleep(5)
    client_progam2 = ServerDiscoveryProtocolClient(8000)
    client_progam2.set_message(json.dumps({'key2':'value2'}))
    client_progam2.start()

    ml.join()
    daemon.join()
    client_progam.join()
