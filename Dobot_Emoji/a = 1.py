from pypylon import pylon
import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
import DobotDllType as dType
import time

api = dType.load()
dType.ConnectDobot(api, "COM3", 115200)

start_time = 0

def transform_coordinates(x_camera, y_camera, regressor_x, regressor_y):
    x_robot = regressor_x.predict(np.array([[x_camera]]))
    y_robot = regressor_y.predict(np.array([[y_camera]]))
    return x_robot[0], y_robot[0]

SMOOTHING_WINDOW_SIZE = 5
smoothed_x = []
smoothed_y = []

robot_coordinates = np.array([(101.64,-201.56),(100.16,-171),(95.44,-137.42),(88.38,-103.58),(58.78,-100),(59.24,-137.94),(64.4,-196.32),(32.5,-194),(31.74,-144.5),(24.89,-96.4),(-7.98,-91.21),(-6.89,-139.27),(-9.44,-192.6),(-44.66,-194.7),(-44.1,-149.2),(-41.3,-104.5),(-78.1,-134.1),(-85.89,-195.26),(-87.66,-159.11),(75.18,-99.85),(73.91,-140.85),(85.88,-186.06),(47.38,-172.56),(36.62,-127.6),(19.61,-94.72),(-12.68,-112.49),(-29.06,-153.91),(-19.11,-192.75),(-59.12,-157.33),(-74.77,-154.62),(-86.7,-197.84),(-90.53,-170.79),(-73.57,-180.21),(-56.28,-148.12)],dtype=np.float64)
image_pixels = np.array([(406,713),(443,828),(445,957),(458,1088),(584,1081),(604,931),(601,718),(746,714),(738,892),(758,1069),(946,1079),(935,907),(940,711),(1104,708),(1118,874),(1126,1039),(1286,950),(1290,718),(1310,859),(508,1192),(504,925),(508,765),(673,791),(711,957),(785,1073),(969,999),(1040,857),(987,717),(1175,780),(1258,863),(1290,706),(1320,810),(1236,768),(1172,882)], dtype=np.float64)

regressor_x = LinearRegression()
regressor_y = LinearRegression()
regressor_x.fit(image_pixels[:, 0].reshape(-1, 1), robot_coordinates[:, 0])
regressor_y.fit(image_pixels[:, 1].reshape(-1, 1), robot_coordinates[:, 1])

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

while True:
    current_time = time.time()
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.blur(gray, (3, 3))

        detected_circles = cv2.HoughCircles(
            gray_blurred, cv2.HOUGH_GRADIENT, 1, 20,
            param1=90, param2=40, minRadius=80, maxRadius=100
        )

        if detected_circles is not None:
            detected_circles = np.uint16(np.around(detected_circles))
            for pt in detected_circles[0, :]:
                a, b, r = pt[0], pt[1], pt[2]

                x_robot, y_robot = transform_coordinates(a, b, regressor_x, regressor_y)

                with open("robot_coordinates.txt", "w") as file:
                    file.write(f"x_robot: {x_robot:.2f}, y_robot: {y_robot:.2f}")

                smoothed_x.append(x_robot)
                smoothed_y.append(y_robot)

                if len(smoothed_x) > SMOOTHING_WINDOW_SIZE:
                    smoothed_x.pop(0)
                    smoothed_y.pop(0)

                x_robot_smoothed = np.mean(smoothed_x)
                y_robot_smoothed = np.mean(smoothed_y)

                name_text = "Robot Coordinates"
                text = f" {name_text}: ({x_robot_smoothed:.2f}, {y_robot_smoothed:.2f})"
                cv2.putText(img, text, (a - 20, b - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

                if name_text == "Robot Coordinates" and start_time == 0:
                    start_time = current_time

                elapsed_time = current_time - start_time if start_time != 0 else 0

                while (name_text == "Robot Coordinates" and elapsed_time >= 5.0):
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 82, -142, 60, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, -2, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, -30, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -2.2, -162, 0, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 83, -164, 114, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 175, 57, 88, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 175, 57, -30, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 199, -38, 88, -15, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)
                    dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                    dType.SetWAITCmd(api, 200, isQueued=1)

                    start_time = current_time
                    name_text = "abc"
                    break

        img = cv2.resize(img, (1023, 1020))
        cv2.imshow("Detected Circle", img)

        k = cv2.waitKey(1)
        if k == 27:
            break

    grabResult.Release()

dType.DisconnectDobot(api)
