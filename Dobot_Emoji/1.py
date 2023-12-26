
from pypylon import pylon
import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
import DobotDllType as dType

# Create a function for coordinate transformation
def transform_coordinates(x_camera, y_camera, regressor_x, regressor_y):
    x_robot = regressor_x.predict(np.array([[x_camera]]))
    y_robot = regressor_y.predict(np.array([[y_camera]]))
    return x_robot[0], y_robot[0]

# Define the number of frames to use for smoothing
SMOOTHING_WINDOW_SIZE = 5
smoothed_x = []
smoothed_y = []

# Connect to the camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Start grabbing continuously with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
converter = pylon.ImageFormatConverter()

# Converting to OpenCV BGR format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# Load the trained regression models
image_pixels = np.array([(590,766),(604,882),(608,1006),(610,1118),(728,1112),(732,996),(718,876),(716,760),(848,1118),(846,998),(846,880),(838,762),(988,1122),(982,1004),(970,894),(976,768),(1114,1124),(1104,1012),(1090,900),(1088,770),(1218,760),(1214,884),(1224,1002),(1226,1118)],dtype=np.float64)
robot_coordinates = np.array([(64.8,-183.3),(59.7,-151),(55.2,-118.3),(50.6,-88.9),(27.8,-85.3),(30,-116.4),(34.8,-150.2),(37.3,-180.8),(7.2,-80.9),(8.8,-115),(9.3,-147),(11.4 ,-180.1),(-15.4,-80.3),(-15.9,-114.9),(-16.1,-145.7),(-17.3,-179.9),(-36.5,-83.7),(-39,-114.6),(-39.6,-145.8),(-41.6,-179.7),(-68.75,-181.45),(-65.5,-149.5),(-63.6,-118.6),(-59.4,-88.3)], dtype=np.float64)
regressor_x = LinearRegression()
regressor_y = LinearRegression()
regressor_x.fit(image_pixels[:, 0].reshape(-1, 1), robot_coordinates[:, 0])
regressor_y.fit(image_pixels[:, 1].reshape(-1, 1), robot_coordinates[:, 1])

# Initialize Dobot API
api = dType.load()
dType.ConnectDobot(api, "COM3", 115200)
dType.SetHOMEParams(api, 199, -38, 88, 14.99, isQueued=0)
dType.SetHOMECmd(api, temp = 0, isQueued = 0)
dType.SetWAITCmd(api, 200, isQueued=1)
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=0)
dType.SetPTPCommonParams(api, 100, 100, isQueued=0)

while True:
    # Capture an image
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Blur the grayscale image
        gray_blurred = cv2.blur(gray, (3, 3))

        # Apply Hough transform to the blurred image
        detected_circles = cv2.HoughCircles(
            gray_blurred, cv2.HOUGH_GRADIENT, 1, 20,
            param1=90, param2=40, minRadius=80, maxRadius=100
        )

        # Draw detected circles and transform their coordinates
        if detected_circles is not None:
            detected_circles = np.uint16(np.around(detected_circles))
            for pt in detected_circles[0, :]:
                a, b, r = pt[0], pt[1], pt[2]

                # Transform camera coordinates to robot coordinates
                x_robot, y_robot = transform_coordinates(a, b, regressor_x, regressor_y)

                # Store the robot coordinates in a file
                with open("robot_coordinates.txt", "w") as file:
                    file.write(f"x_robot: {x_robot:.2f}, y_robot: {y_robot:.2f}")

                # Smooth the coordinates using a simple moving average
                smoothed_x.append(x_robot)
                smoothed_y.append(y_robot)

                if len(smoothed_x) > SMOOTHING_WINDOW_SIZE:
                    smoothed_x.pop(0)
                    smoothed_y.pop(0)

                x_robot_smoothed = np.mean(smoothed_x)
                y_robot_smoothed = np.mean(smoothed_y)

                # Display the smoothed robot coordinates
                text = f"Robot Coordinates: ({x_robot_smoothed:.2f}, {y_robot_smoothed:.2f})"
                cv2.putText(img, text, (a - 20, b - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, -20, -15, isQueued=1)
                dType.SetWAITCmd(api, 200, isQueued=1)
                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, -31.2, -15, isQueued=1)
                dType.SetWAITCmd(api, 200, isQueued=1)
                dType.SetEndEffectorSuctionCup(api, True, True, isQueued=1)
                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_robot_smoothed, y_robot_smoothed, 88, -15, isQueued=1)
                dType.SetWAITCmd(api, 200, isQueued=1)
                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -84.7, -157.7, 88, -15, isQueued=1)
                dType.SetWAITCmd(api, 200, isQueued=1)
                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -84.7, -157.7, -30, -15, isQueued=1)
                dType.SetWAITCmd(api, 200, isQueued=1)
                dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -84.7, -157.7, 88, -15, isQueued=1)
                dType.SetWAITCmd(api, 200, isQueued=1)

        # Display the result image
        img_resized = cv2.resize(img, (1023, 1020))
        cv2.imshow("Detected Circle", img_resized)

        k = cv2.waitKey(1)
        if k == 27:
            break

    grabResult.Release()

# Disconnect the Dobot robot
dType.DisconnectDobot(api)

# Release the camera resources    
camera.StopGrabbing()
cv2.destroyAllWindows()