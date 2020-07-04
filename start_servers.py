#Progressive imports in this file
from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerDiscoveryProtocolDaemon
from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerInformationMessage
from ServerDiscoveryProtocol.ServerDiscoveryProtocol import BROADCAST_PORT

### Starting Daemon ###
sdp_daemon_listen_port = 7878
sdp_daemon = ServerDiscoveryProtocolDaemon('192.168.0.255', BROADCAST_PORT, sdp_daemon_listen_port)
sdp_daemon.start()

from MaestroServerStarter.ServerStarter import ServerStarter
firestarter = ServerStarter('server_starter.json')

### Sricam Server ###
# from SricamInputNode import SricamInputNode
# sricam_input_node_port = 8002
# sricam_input_node = SricamInputNode.SricamInputNode("rtsp://192.168.0.27/onvif1", sricam_input_node_port)
# sricam_input_node.start()


# from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerDiscoveryProtocolClient
# sdp_client_sricam = ServerDiscoveryProtocolClient(sdp_daemon_listen_port)
# sdp_client_sricam.set_message(ServerInformationMessage(SricamInputNode.NODE_IDENTITY, sricam_input_node_port, '1.0'))
# sdp_client_sricam.start()

### FaceDetectNode Server ###
# from FaceDetectNode import FaceDetectNode
# face_detect_node_port = 8001
# face_detect_node = FaceDetectNode.FaceDetectNode(face_detect_node_port, "./FaceDetectNode/face_detection_model")
# face_detect_node.start()

# from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerDiscoveryProtocolClient
# sdp_client_facedetect = ServerDiscoveryProtocolClient(sdp_daemon_listen_port)
# sdp_client_facedetect.set_message(ServerInformationMessage(FaceDetectNode.NODE_IDENTITY,face_detect_node_port, '1.0'))
# sdp_client_facedetect.start()

### SpeakerOutputNode ###
# from SpeakerOutputNode import SpeakerOutputNode
# from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerDiscoveryProtocolClient
# speaker_node_port = 8003
# speaker_node = SpeakerOutputNode.SpeakerOutputNode(speaker_node_port)
# speaker_node.start()

# sdp_client_speakernode = ServerDiscoveryProtocolClient(sdp_daemon_listen_port)
# sdp_client_speakernode.set_message(ServerInformationMessage(SpeakerOutputNode.NODE_IDENTITY,speaker_node_port, '1.0'))
# sdp_client_speakernode.start()

# from FaceRecognitionNode import FaceRecognitionNode
# from ServerDiscoveryProtocol.ServerDiscoveryProtocol import ServerDiscoveryProtocolClient
# face_recognition_node_port = 8004
# face_recognition_node = FaceRecognitionNode.FaceRecognitionNode(face_recognition_node_port, 
#     embedder_model='FaceRecognitionNode/openface_nn4.small2.v1.t7', 
#     recognizer_file='FaceRecognitionNode/custom_recognizer.pickle',
#     label_encoder_file='FaceRecognitionNode/custom_label_encoder.pickle')
# face_recognition_node.start()

# sdp_client_face_recognition_node = ServerDiscoveryProtocolClient(sdp_daemon_listen_port)
# sdp_client_face_recognition_node.set_message(ServerInformationMessage(FaceRecognitionNode.NODE_IDENTITY,face_recognition_node_port, '1.0'))
# sdp_client_face_recognition_node.start()


### Joining ### 
sdp_daemon.join()
# sricam_input_node.join()
# sdp_client_facedetect.join()
# face_detect_node.join()
# sdp_client_facedetect.join()
