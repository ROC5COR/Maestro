from Maestro.MaestroScenarioV2 import MaestroScenarioV2
from Maestro.MaestroUtils import *
import time
import cv2
import numpy as np
import random

class SricamFaceSpeaker(MaestroScenarioV2):
    def __init__(self):
        super().__init__("SricamFaceDetectV2")
        self.dependencies = ['SricamInputNode', 'FaceDetectNode', 'SpeakerOutputNode']

    def run(self):
        face_detected = False
        while True:
            frame = make_get('SricamInputNode', '/frame')
            detections = make_post('FaceDetectNode', '/process', {'mode':'image'}, frame)
            if len(detections) > 0:
                for detection in detections:
                    if detection['type'] == 'image/rgb':
                        data = np.array(detection['data'])
                        cv2.imwrite(time.asctime().replace(' ','-')+str(random.randint(100,200))+'.jpg',data)
                        print("Image written")
                    else:
                        print("Can't write image of type:",detection['type'])

                if not face_detected:
                    pass
                    #make_post('SpeakerOutputNode', '/output_text', {'data':"Un humain est dans la cuisine"}, None)
                    
            print("Face detected: ",len(detections))
            
            time.sleep(0.5)
