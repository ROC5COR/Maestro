from Maestro.MaestroScenarioV2 import MaestroScenarioV2
from Maestro.MaestroUtils import *
import time

class SricamFaceDetect(MaestroScenarioV2):
    def __init__(self):
        super().__init__("SricamFaceDetectV2")
        self.dependencies = ['SricamInputNode', 'FaceDetectNode']

    def run(self):
        while True:
            frame = make_get('SricamInputNode', '/frame')
            detection = make_post('FaceDetectNode', '/process', {'mode':'image'}, frame)
            if len(detection) > 0:
                print("Face detected: ",len(detection))
            
            time.sleep(0.5)
            
                
