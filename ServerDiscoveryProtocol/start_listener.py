from ServerDiscoveryProtocol import ServerDiscoveryProtocolListener

#def message_received(data):
#    print("Message received: ",data)

sdp_listener = ServerDiscoveryProtocolListener(6767, show_debug=False, show_info=True)
sdp_listener.start()

#ml = MessageListener(6767, show_debug=True, show_info=True)
#ml.set_callback(message_received)
#ml.start()
#ml.join()
