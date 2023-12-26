from pypylon import pylon
import cv2
import numpy as np
from ultralytics import YOLO
import DobotDllType as dType
from Tran_matrix2 import optimal_transformation_matrix
import time

api = dType.load()
dType.ConnectDobot(api, "COM3", 115200)
waiting_time = None

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

model = YOLO('D:/Face_Icon/runs/runs/detect/train/weights/best.pt')

emotions = {
    '0': {'offset': (167)},
    '1': {'offset': ( 113) },
    '2': {'offset': (58) },
    '3': {'offset': (3) },
    '4': {'offset': (-50) }
}
z_values = [-57, -57, -57, -57, -57]

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()
        img_resized = cv2.resize(img, (1023, 1020))
        a1, b1, a2, b2 = 159,208,779,676
        cropped_image = img_resized[b1:b2, a1:a2]
        results = model(cropped_image)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]
                x1, y1, x2, y2 = map(int, b)
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                c = int(box.cls)
                id = str(c)
                name = model.names[c]
                print(x1, y1, x2, y2, id, name)
                cv2.rectangle(cropped_image, (x1, y1), (x2, y2), (255, 0, 255), 2)
                cv2.putText(cropped_image, name, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 0))

                if id == '4':  # 
                    emotion_info = emotions.get(id)
                    if emotion_info:
                        camera_coordinate = np.array([center_x, center_y])
                        robot_coordinate = np.dot(optimal_transformation_matrix, np.hstack((camera_coordinate, [1])))
                        robot_x, robot_y = robot_coordinate[:2]
                        print(f"Robot Arm Coordinate: ({robot_x}, {robot_y})")

                        if waiting_time is None:
                            waiting_time = time.time() + 4
                        elif time.time() >= waiting_time:
                            allow_prediction = False
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 233, 127, 30,70, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 210, -6, 15,70, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, 15, 70, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, -32,70, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, 15, 70, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 210, -6, 15,70, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 233, 127, 30,70, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,  20, 220, 70, 70,isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, emotion_info['offset'],242, 70, 177, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,  emotion_info['offset'],242, z_values[c], 177, isQueued=1)
                            dType.SetWAITCmd(api, 200, isQueued=1)
                            dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                            dType.SetWAITCmd(api, 200, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, emotion_info['offset'],242, 70, 177, isQueued=1)
                            dType.SetWAITCmd(api, 100, isQueued=1)
                            dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 20, 220, 70, 70, isQueued=1)
                            time.sleep(6)


                            waiting_time = None
                            allow_prediction = True
                            z_values[c] += 4.5

        name_text = "RB_Coordinate"
        text = f"{name_text}:({robot_x:.3f}, {robot_y:.3f})"
        cv2.putText(cropped_image, text, (int(center_x / 2 - 2), int(center_y / 2 + 100)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 2)
        cv2.imshow("YOLOv8 Inference", cropped_image)

        k = cv2.waitKey(1)
        if k == 27:
            break

    grabResult.Release()

camera.StopGrabbing()
cv2.destroyAllWindows()
