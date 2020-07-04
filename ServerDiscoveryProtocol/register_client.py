import sys
from ServerDiscoveryProtocol import ServiceDiscoveryProtocolClient

if len(sys.argv) != 2:
    print("You have to specify a message to broadcast")

message = sys.argv[1]

client_progam = ServiceDiscoveryProtocolClient(8000, show_info=True, show_debug=True)
client_progam.set_message(message)
client_progam.start()
client_progam.join()
