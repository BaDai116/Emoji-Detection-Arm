import DobotDllType as dType
api = dType.load()
dType.ConnectDobot(api, "COM3", 115200)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 199, -38, 88, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -53.5, -100.28, -28, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 83.5, -165, 115, -15, isQueued=1)
# dType.SetWAITCmd(api, 200, isQueued=1)
# dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)

dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
dType.DisconnectDobot(api)