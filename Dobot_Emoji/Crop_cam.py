from pypylon import pylon
import cv2
import numpy as np
from ultralytics import YOLO
import DobotDllType as dType
from Trans_Matrix import optimal_transformation_matrix
import time

api = dType.load()
dType.ConnectDobot(api, "COM4", 115200)
waiting_time = None

# Kết nối camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# Load model YOLO
model = YOLO('runs/runs/detect/train/weights/best.pt')
# Tạo một dictionary để ánh xạ tên cảm xúc và thông tin liên quan
emotions = {
    '0': {'offset': (-35)},
    '1': {'offset': ( 0) },
    '2': {'offset': (35) },
    '3': {'offset': (70) },
    '4': {'offset': (105) }
}
z_values = [-62, -62, -62, -62, -62]

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()
        img_resized = cv2.resize(img, (1023, 1020))
        a1, b1, a2, b2 = 167,198,784,665
        cropped_image = img_resized[b1:b2, a1:a2]
        results = model(cropped_image)

        # for r in results:
        #     boxes = r.boxes
        #     for box in boxes:
        #         b = box.xyxy[0]
        #         x1, y1, x2, y2 = map(float, b)
        #         center_x = (x1 + x2) / 2
        #         center_y = (y1 + y2) / 2
        #         c = int(box.cls)
        #         name = model.names[c]
        #         id = str(c)
        #         print(x1, y1, x2, y2, id, name)
                # cv2.rectangle(cropped_image, (x1, y1), (x2, y2), (255, 0, 255), 2)
                # cv2.putText(cropped_image, name, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 0))

        #         emotion_info = emotions.get(id)
        #         if emotion_info:
        #             camera_coordinate = np.array([center_x, center_y])
        #             robot_coordinate = np.dot(optimal_transformation_matrix, np.hstack((camera_coordinate, [1])))
        #             robot_x, robot_y = robot_coordinate[:2]
        #             print(f"Robot Arm Coordinate: ({robot_x}, {robot_y})")

        #             if waiting_time is None:
        #                 waiting_time = time.time() + 3
        #             elif time.time() >= waiting_time:
        #                 allow_prediction = False
        #                 dType.SetPTPCommonParams(api, 250, 250, isQueued=0)
        #                 dType.SetPTPCommonParams(api, 250, 250, isQueued=0)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 18, -202, 15, 82.2, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, 15, 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, -31, 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, 15, 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 18, -202, 15,82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 240, emotion_info['offset'], 88, 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 240, emotion_info['offset'], z_values[c], 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 400, isQueued=1)
        #                 dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
        #                 dType.SetWAITCmd(api, 400, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 240, emotion_info['offset'], 88,
        #                                 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, 82.2, isQueued=1)
        #                 dType.SetWAITCmd(api, 200, isQueued=1)
        #                 time.sleep(14)


        #                 waiting_time = None
        #                 allow_prediction = True
        #                 z_values[c] += 4.3

        # name_text = "camera_"
        # text = f"{name_text}:({center_x:.1f}, {center_y:.1f})"
        # cv2.putText(cropped_image, text, (int(center_x / 2 - 2), int(center_y / 2 + 100)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.imshow("YOLOv8 Inference", cropped_image)

        k = cv2.waitKey(1)
        if k == 27:
            break

    grabResult.Release()

camera.StopGrabbing()
cv2.destroyAllWindows()