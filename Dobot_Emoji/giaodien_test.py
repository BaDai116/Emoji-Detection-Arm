import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import threading
import signal
import subprocess

root = tk.Tk()
root.title("Ứng dụng Điều khiển")

model_ai_detec_running = False
model_ai_detec_process = None
camera_image_label = None

# Tạo một kiểu cho nút
style = ttk.Style()
style.configure("Custom.TButton", background="green")

def run_script(script_name):
    global model_ai_detec_running, model_ai_detec_process

    if script_name == "Model_ai_detec.py":
        if not model_ai_detec_running:
            model_ai_detec_process = subprocess.Popen(["python", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
            model_ai_detec_running = True
            update_camera_frames()
        else:
            os.kill(model_ai_detec_process.pid, signal.SIGTERM)
            model_ai_detec_running = False

def update_button_states():
    if model_ai_detec_running:
        btn_model_ai_detec.config(text="Stop Model_ai_detec", style="Custom.TButton")
    else:
        btn_model_ai_detec.config(text="Start Model_ai_detec", style="Custom.TButton")

    root.after(100, update_button_states)

def update_camera_frames():
    global model_ai_detec_process, camera_image_label, model_ai_detec_running
    if model_ai_detec_running:
        frame = model_ai_detec_process.stdout.readline()
        if not frame:
            model_ai_detec_running = False
            btn_model_ai_detec.config(text="Start Model_ai_detec", style="Custom.TButton")
        else:
            try:
                frame = frame.strip()  # Loại bỏ các khoảng trắng không cần thiết
                frame_data = bytes.fromhex(frame)  # Chuyển đổi thành dãy bytes
                image = Image.frombytes('RGB', (1023, 1020), frame_data, 'raw')
                photo = ImageTk.PhotoImage(image=image)
                camera_image_label.config(image=photo)
                camera_image_label.image = photo
                root.after(10, update_camera_frames)
            except ValueError:
                print("Invalid hexadecimal data:", frame)
    else:
        camera_image_label.config(image="")
        root.after(1000, update_camera_frames)


btn_model_ai_detec = ttk.Button(root, text="Start Model_ai_detec", command=lambda: run_script("Model_ai_detec.py"), style="Custom.TButton")
btn_model_ai_detec.pack(pady=10)

camera_image_label = ttk.Label(root)
camera_image_label.pack()

root.after(100, update_button_states)
root.mainloop()
