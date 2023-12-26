from pypylon import pylon
import cv2
import numpy as np
from ultralytics import YOLO
import DobotDllType as dType
from Trans_Matrix import optimal_transformation_matrix
import time
import tkinter as tk
from tkinter import Entry, Label, Button

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
    '0': {'offset': (-35)},  
    '1': {'offset': (0)},    
    '2': {'offset': (35)},   
    '3': {'offset': (70)},   
    '4': {'offset': (105)}   
}
z_values = [-62, -62, -62, -62, -62]

# Create an empty list to store the user-defined order
user_defined_order = []

def run_code():
    global waiting_time  # Khai báo biến global để tránh lỗi UnboundLocalError
    for item in user_defined_order:
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
                        id = str(c)
                        name = model.names[c]
                        print(x1, y1, x2, y2, id, name)
                        cv2.rectangle(cropped_image, (x1, y1), (x2, y2), (255, 0, 255), 2)
                        cv2.putText(cropped_image, name, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 0))

                        # Check if the emotion is in the desired order
                        if id == item:
                            emotion_info = emotions.get(id)
                            if emotion_info:
                                camera_coordinate = np.array([center_x, center_y])
                                robot_coordinate = np.dot(optimal_transformation_matrix, np.hstack((camera_coordinate, [1])))
                                robot_x, robot_y = robot_coordinate[:2]
                                print(f"Robot Arm Coordinate: ({robot_x}, {robot_y})")

                                if waiting_time is None:
                                    waiting_time = time.time() + 3
                                elif time.time() >= waiting_time:
                                    allow_prediction = False
                                    dType.SetPTPCommonParams(api, 200, 200,isQueued=0)
                                    dType.SetPTPCommonParams(api, 200, 200, isQueued=0)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -6, -250, 15, -15, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, 15,-15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, -31, -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetEndEffectorSuctionCup(api,True ,True , isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, robot_x, robot_y, 15, -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, -6, -250, 15, -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 240, emotion_info['offset'], 88, -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 240, emotion_info['offset'], z_values[c], -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetEndEffectorSuctionCup(api, True, False, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 240, emotion_info['offset'], 88, -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 257.65, -49.15, 88, -15, isQueued=1)
                                    dType.SetWAITCmd(api, 200, isQueued=1)
                                    time.sleep(16)

                        

                                    waiting_time = None
                                    allow_prediction = True
                                    z_values[c] += 4.3

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

# Function to start the GUI
def start_gui():
    root = tk.Tk()
    root.title("Auto Order")

    def on_run_button_click():
        order = order_entry.get()
        global user_defined_order
        user_defined_order = list(order)  # Convert the input string to a list of characters
        print(f"Running code with order: {user_defined_order}")
        run_code()

    label = Label(root, text="Enter the order:")
    label.pack()

    order_entry = Entry(root)
    order_entry.pack()

    run_button = Button(root, text="Run Code", command=on_run_button_click)
    run_button.pack()

    root.mainloop()

if __name__ == "__main__":
    start_gui()
