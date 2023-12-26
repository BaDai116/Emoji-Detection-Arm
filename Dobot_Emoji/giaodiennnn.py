import tkinter as tk
from tkinter import ttk
import os
import threading
import signal
import subprocess
import cv2
from PIL import Image, ImageTk  # Import thư viện cho việc hiển thị hình ảnh

root = tk.Tk()
root.title("Ứng dụng Điều khiển")

model_ai_detec_running = False
disconect_running = False
sethome_running = False
model_ai_detec_process = None
camera = None  # Biến để lưu trữ kết nối camera

def run_script(script_name):
    global model_ai_detec_running, disconect_running, sethome_running, model_ai_detec_process

    if script_name == "Model_ai_detec.py":
        if not model_ai_detec_running:
            model_ai_detec_process = subprocess.Popen(["python", script_name])
            model_ai_detec_running = True
            start_camera_stream()  # Bắt đầu luồng hiển thị camera
        else:
            os.kill(model_ai_detec_process.pid, signal.SIGTERM)
            model_ai_detec_running = False

# Hàm này sẽ hiển thị hình ảnh từ camera trong cửa sổ giao diện
def start_camera_stream():
    global camera
    camera = cv2.VideoCapture(0)  # Khởi tạo camera (sử dụng camera số 0)

    def update_camera_frame():
        _, frame = camera.read()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            label.config(image=photo)
            label.image = photo
            label.after(10, update_camera_frame)  # Cập nhật hình ảnh mỗi 10ms

    update_camera_frame()

def update_button_states():
    if model_ai_detec_running:
        btn_model_ai_detec.config(text=" Model_ai_detec.py", bg="red")
    else:
        btn_model_ai_detec.config(text=" Model_ai_detec.py", bg="SystemButtonFace")

    if disconect_running:
        btn_disconect.config(state=tk.DISABLED, text="disconect y", bg="green")
    else:
        btn_disconect.config(state=tk.NORMAL, text=" disconect.py", bg="SystemButtonFace")

    if sethome_running:
        btn_sethome.config(state=tk.DISABLED, text="sethome ", bg="green")
    else:
        btn_sethome.config(state=tk.NORMAL, text="sethome.py", bg="SystemButtonFace")

    root.after(100, update_button_states)

btn_model_ai_detec = ttk.Button(root, text="Auto_Robot", command=lambda: run_script("Model_ai_detec.py"))
btn_model_ai_detec.pack(pady=10)

btn_disconect = ttk.Button(root, text="Disconnect", command=lambda: run_script("disconect.py"))
btn_disconect.pack(pady=10)

btn_sethome = ttk.Button(root, text="SetHome", command=lambda: run_script("sethome.py"))
btn_sethome.pack(pady=10)

status_label = ttk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=10)

label = tk.Label(root)  # Khung để hiển thị hình ảnh từ camera
label.pack()

root.after(100, update_button_states)
root.mainloop()
