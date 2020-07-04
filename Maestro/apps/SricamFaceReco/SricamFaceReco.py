from Maestro.MaestroScenarioV2 import MaestroScenarioV2
from Maestro.MaestroUtils import *
import time
import json

class SricamFaceRecognition(MaestroScenarioV2):
    def __init__(self):
        super().__init__("SricamFaceRecognitiontV1")
        self.dependencies = ['SricamInputNode', 'FaceDetectNode', 'FaceRecognitionNode']

    def run(self):
        while True:
            frame = make_get('SricamInputNode', '/frame')
            detections = make_post('FaceDetectNode', '/process', {'mode':'image'}, frame)
            if detections is not None and len(detections) > 0:
                print("Face detected: ",len(detections))
                for detection in detections:
                    if detection['type'] == 'image/rgb':
                        img_data = detection['data']
                        res = make_post('FaceRecognitionNode', '/process', {'from':'rgb'}, json.dumps(img_data))
                        print(res)
                    elif detection['type'] == 'image/jpg':
                        img_data = detection['data']
                        res = make_post('FaceRecognitionNode', '/process', {'from':'jpg'}, json.dumps(img_data))
                        print(res)
                    else:
                        print("Can't face detection from image type",detection['type'])
                    
            
            time.sleep(0.5)
            
                
