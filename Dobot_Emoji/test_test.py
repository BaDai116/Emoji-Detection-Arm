import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
from ultralytics import YOLO
import time
import DobotDllType as dType
from pypylon import pylon
import os
def transform_coordinates(camera_x, camera_y, regressor_x, regressor_y):
    x_robot = regressor_x.predict(np.array([[camera_x]]))
    y_robot = regressor_y.predict(np.array([[camera_y]]))
    return x_robot[0], y_robot[0]

def setup_dobot():
    api = dType.load()
    dType.ConnectDobot(api, "COM3", 115200)
    return api

def initialize_camera():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    return camera, converter

def initialize_regression_models():
    image_pixels = np.array([(40.75,148.69),(44.87,208.65),(38.70,285.86),(30.84,348.57),(111,315.34),(126.27,233.34),(109.20,134.70),(184,344.88),(190.43,258.78),(212.20,188.28),(188.20,132.50),(247.40,242.0),(274.5,339.6),(277.25,125.3),(305.70,191.14),(304.5,266.85),(354.7,346.25),(362,113.1),(380.99,183.16),(426.2,252.6),(445.06,341.14),(529.63,347.94),(502,276.42),(463.6,181.2),(441.25,107.26),(523.38,116.2),(526.4,185.2),(573.16,221.89),(581.18,294.72),(573.24,136.62)],dtype=np.float64)
    robot_coordinates= np.array([(264.44,152.78),(230.47,149.11),(185.99,152.57),(149.0,157.98),(168.32,108.79),(215.86,100.7),(272.37,110.76),(153.84,67.08),(200.40,64.09),(241.51,51.53),(273.44,65.64),(212.3732,31.52),(157.16,15.36),(276.61,14.32),(238.80,-1.1),(198.14,-20.39),(152.97,-29.40),(284.88,-33.18),(243.94,-43.38),(205.38,-69.68),(156.32,-80.83),(151.20,-128.18),(192.55,-112.43),(245.83,-90.43),(288.32,-78.44),(282.56,-125.23),(243.08,-125.84),(222.87,-153.43),(181.90,-158.44),(271.57,-153.73)],dtype=np.float64)
    # image_pixels = np.array([(32,354),(34,286),(38,218),(38,159),(55,334),(58,300),(60,270),(56,222),(60,172),(99,156),(100,186),(98,234),(102,280),(104,310),(101,335),(108,359),(142,317),(152,264),(152,220),(156,156),(204,154),(210,194),(208,252),(224,302),(233,356),(264,346),(286,290),(284,242),(290,190),(296,152),(336,152),(342,188),(347,256),(352,318),(366,356),(410,344),(420,295),(427,233),(430,188),(444,154),(478,154),(480,212),(484,255),(484,305),(514,301),(515,251),(528,156)], dtype=np.float64)
    regressor_x = LinearRegression()
    regressor_y = LinearRegression()
    
    
    regressor_x.fit(image_pixels[:, 0].reshape(-1, 1), robot_coordinates[:, 0])
    regressor_y.fit(image_pixels[:, 1].reshape(-1, 1), robot_coordinates[:, 1])
    return regressor_x, regressor_y



def main():
    api = setup_dobot()
    camera, converter = initialize_camera()
    regressor_x, regressor_y = initialize_regression_models()

    SMOOTHING_WINDOW_SIZE = 5
    smoothed_x = []
    smoothed_y = []

    threshold = 0.5
    image_count = 0
    model = YOLO('D:/Dobot_demo/runs/runs/detect/train/weights/best.pt')

    # Thời gian chờ
    waiting_time = None
    allow_prediction = True
    last_results = None  # Biến lưu trữ kết quả đoán trước đó

    while True:
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            img = image.GetArray()
            img_resized = cv2.resize(img, (1023, 1020))
            a1, b1, a2, b2 = 150, 200, 775, 670
            cropped_image = img_resized[b1:b2, a1:a2]
            if allow_prediction :
                results = model(cropped_image)
                

                if len(results) > 0:
                    r = results[0]
                    boxes = r.boxes.xyxy
                    if len(boxes) > 0:
                        box = boxes[0]
                        x1, y1, x2, y2 = box
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        

                        center_x1, center_y1 = transform_coordinates(center_x, center_y, regressor_x, regressor_y)

                        smoothed_x.append(center_x1)
                        smoothed_y.append(center_y1)

                        if len(smoothed_x) > SMOOTHING_WINDOW_SIZE:
                            smoothed_x.pop(0)
                            smoothed_y.pop(0)

                        x_robot_smoothed = np.mean(smoothed_x)
                        y_robot_smoothed = np.mean(smoothed_y)

                        cropped_image = results[0].plot()

                        name_text = "Robot Coordinates"
                        text = f"{name_text}:({x_robot_smoothed:.3f}, {y_robot_smoothed:.3f})"
                        
                        cv2.putText(cropped_image, text, (int((center_x) / 2 - 2), int((center_y) / 2 +50)), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                                    (255, 255, 255), 2)

                        # if last_results is not None and not np.array_equal(last_results, results):
                        #     cv2.destroyAllWindows()

                        cv2.imshow("YOLOv8 Inference", cropped_image)

                        last_results = results

                        if name_text == "Robot Coordinates":
                            if waiting_time is None:
                                waiting_time = time.time() + 4
                                # os.system("cls")
                            elif time.time() >= waiting_time:
                                # os.system('cls')
                                allow_prediction = False
                                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 210, 160, 70,70, isQueued=1)
                                dType.SetWAITCmd(api, 200, isQueued=1)

                                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, 15, 70, isQueued=1)
                                dType.SetWAITCmd(api, 200, isQueued=1)
                                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, -31, 70, isQueued=1)
                                dType.SetWAITCmd(api, 200, isQueued=1)
                                dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)
                                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, 50, 70, isQueued=1)
                                dType.SetWAITCmd(api, 200, isQueued=1)
                                # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 18, -202, 55, -15, isQueued=1)
                                # dType.SetWAITCmd(api, 200, isQueued=1)
                                # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, -15, isQueued=1)
                                # dType.SetWAITCmd(api, 200, isQueued=1)
                                # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 238, -27, -33, -15, isQueued=1)
                                # dType.SetWAITCmd(api, 200, isQueued=1)
                                # dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                                # dType.SetWAITCmd(api, 200, isQueued=1)
                                # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, -15, isQueued=1)
                                # dType.SetWAITCmd(api, 200, isQueued=1)
                                # dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                                # dType.SetWAITCmd(api, 200, isQueued=1)
                                time.sleep(11)
                                waiting_time = None  # Đặt lại thời gian chờ
                                allow_prediction = True
                                

        k = cv2.waitKey(1)
        if k == 27:
            break

        grabResult.Release()

    dType.DisconnectDobot(api)

if __name__ == "__main__":
    main()
