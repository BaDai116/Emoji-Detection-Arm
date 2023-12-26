import DobotDllType as dType
import cv2

api = dType.load()
dType.ConnectDobot(api, "COM3", 115200)

dType.SetHOMEParams(api, 199, -38, 88, 14.99, isQueued=0)
dType.SetHOMECmd(api, temp = 0, isQueued = 0)
dType.SetWAITCmd(api, 200, isQueued=1)
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=0)
dType.SetPTPCommonParams(api, 100, 100, isQueued=0)

dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 14.2, -157.7, 3, -15, isQueued=1)
dType.SetWAITCmd(api, 200, isQueued=1)
dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -33.26, -125.17, 3, -15, isQueued=1)
dType.SetWAITCmd(api, 200, isQueued=1)
dType.DisconnectDobot(api)


cv2.destroyAllWindows()
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 199, -38, 88, 14.99, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -4.79, -192.39, 3, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -34.4, -181.7, 3, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 43.45, -139.57, 3, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -57, -172, -20, -15, isQueued=1)
dType.SetWAITCmd(api, 200, isQueued=1)

# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 124, 36, -18, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 130, 25, 89, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,120, 0, -18, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
# dType.DisconnectDobot(api)
















# while True:


#     dType.ConnectDobot(api, "COM3", 115200)
#     dType.SetHOMEParams(api, 200, 200, 200, 200, isQueued=1)
#     dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
#     dType.SetPTPCommonParams(api, 100, 100, isQueued=1)
#     dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 120, 10, 55, 10, isQueued=1)
#     dType.SetWAITCmd(api, 200, isQueued=1)
#     dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 120, 10, -66, 10, isQueued=1)
#     dType.SetWAITCmd(api, 200, isQueued=1)
#     dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)
#     dType.SetWAITCmd(api, 800, isQueued=1)
#     dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 120, 10, 55, 10, isQueued=1)
#     dType.SetWAITCmd(api, 200, isQueued=1)
#     dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 120, 90, 55, 10, isQueued=1)
#     dType.SetWAITCmd(api, 200, isQueued=1)
#     dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 120, 90, -66, 10, isQueued=1)
#     dType.SetWAITCmd(api, 200, isQueued=1)
    
#     dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
#     dType.SetWAITCmd(api, 200, isQueued=1)
#     dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 120, 90, 55, 10, isQueued=1)
#     dType.SetWAITCmd(api, 200, isQueued=1)
#     break

dType.DisconnectDobot(api)


cv2.destroyAllWindows()



