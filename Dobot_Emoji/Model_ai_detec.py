from pypylon import pylon
import cv2
import numpy as np
import os
from ultralytics import YOLO
import DobotDllType as dType
from Trans_Matrix import optimal_transformation_matrix
import torch
import time

api = dType.load()
dType.ConnectDobot(api, "COM3", 115200)
waiting_time = None

# Kết nối camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# Load model YOLO
model = YOLO('D:/Face_Icon/runs/runs/detect/train/weights/best.pt')

# Tạo một dictionary để ánh xạ tên cảm xúc và thông tin liên quan
emotions = {
    'angry': {'offset': (-35)},
    'cry': {'offset': ( 0) },
    'love': {'offset': (35) },
    'sad': {'offset': (70) },
    'smile': {'offset': (105) }
}

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()
        img_resized = cv2.resize(img, (1023, 1020))
        a1, b1, a2, b2 = 150, 190, 770, 670
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
                name = model.names[c]
                print(x1, y1, x2, y2, c, name)
                cv2.rectangle(cropped_image, (x1, y1), (x2, y2), (255, 0, 255), 2)
                cv2.putText(cropped_image, name, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 0))

                emotion_info = emotions.get(name)
                if emotion_info:
                    camera_coordinate = np.array([center_x, center_y])
                    robot_coordinate = np.dot(optimal_transformation_matrix, np.hstack((camera_coordinate, [1])))
                    robot_x, robot_y = robot_coordinate[:2]
                    print(f"Robot Arm Coordinate: ({robot_x}, {robot_y})")

                    if waiting_time is None:
                        waiting_time = time.time() + 2
                    elif time.time() >= waiting_time:
                        allow_prediction = False
                        dType.SetPTPCommonParams(api, 400, 400,isQueued=0)
                        dType.SetPTPCommonParams(api, 300, 300, isQueued=0)
                        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 18, -202, 55, -15, isQueued=1)
                        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, -2,-15, isQueued=1)
                        dType.SetWAITCmd(api, 200, isQueued=1)
                        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, -31, -15, isQueued=1)
                        dType.SetWAITCmd(api, 200, isQueued=1)
                        dType.SetEndEffectorSuctionCup(api,True ,True , isQueued=1)
                        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 18, -202, 55, -15, isQueued=1)
                        dType.SetWAITCmd(api, 200, isQueued=1)
                        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, -15, isQueued=1)
                        dType.SetWAITCmd(api, 200, isQueued=1)
                        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 240, emotion_info['offset'],-46 , -15, isQueued=1)
                        dType.SetWAITCmd(api, 200, isQueued=1)
                        dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                        dType.SetWAITCmd(api, 200, isQueued=1)
                        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, -15, isQueued=1)
                        dType.SetWAITCmd(api, 200, isQueued=1)
                        time.sleep(12)

                        waiting_time = None
                        allow_prediction = True

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