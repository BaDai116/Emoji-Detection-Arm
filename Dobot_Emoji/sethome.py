from pypylon import pylon
import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
import DobotDllType as dType

api = dType.load()
dType.ConnectDobot(api, "COM3", 115200)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, -15, isQueued=1)
#                             dType.SetWAITCmd(api, 200, isQueued=1)
dType.SetHOMEParams(api, 257.65, -49.15, 88, 15, isQueued=0)

dType.SetHOMECmd(api, temp = 0, isQueued = 0)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 18, -202, 55, 82.2, isQueued=1)
dType.SetWAITCmd(api, 200, isQueued=1)
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=0)
dType.SetPTPCommonParams(api, 200, 200,isQueued=0)
dType.SetPTPCommonParams(api, 200, 200, isQueued=0)

