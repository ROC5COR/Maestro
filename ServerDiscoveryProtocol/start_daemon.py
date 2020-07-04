from ServerDiscoveryProtocol import ServerDiscoveryProtocolDaemon

print("Starting Daemon")
daemon = ServerDiscoveryProtocolDaemon("192.168.0.255", 6767, 7878)
daemon.start()
daemon.join()
