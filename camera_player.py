# Copyright (c) 2024, OPENZEKA All rights reserved.

import PySimpleGUI as sg
from PIL import Image, ImageTk
from client_se import ClientSE
import time
import json

is_first = True
is_connected = False
cam_types = ['CSI','USB', 'RTSP/HTTP']
cse_target = "http://0.0.0.0:7005"
cam_path = "http://renzo.dyndns.tv/mjpg/video.mjpg"
interframe_duration = 1/33

client:ClientSE = None

def connect(client, cse_target, cam_type, cam_path, token):
    client  = ClientSE(cse_target, token)
    ret, msg = client.check()
    print(msg)
    if not ret :
        data = json.loads(msg)
        if 'error' in data:
            sg.popup(data['error'], title="Error")
        return None
    print(cam_type)
    if cam_type == cam_types[0]:
        client.open_csi(cam_path,sensor_mode=4, width=1920, height=1080, fps=30)
    elif cam_type == cam_types[1]:
        client.open_usb(cam_path, width=640, height=480, fps=30)
    else:
        client.open_ip(cam_path)
    client.run()

    return client

sg.theme('BluePurple')

layout = [[sg.Text(text="Token: "), sg.Input(default_text="Enter your token here", pad=((76,0),(0,0)), size=(50,5), key="TOKEN")],
         [sg.Text(text="Stream Engine IP: "), sg.Input(default_text=cse_target, size=(50,5), key="TARGET_IP")],
         [sg.Text(text="Camera Type: "), sg.Combo(values=cam_types, pad=((29,0),(0,0)), default_value=cam_types[2], size=(10,3), key="CAM_TYPE")],
         [sg.Text(text="Camera Source: ", enable_events=True, key="ON_CHANGE"),
          sg.Input(default_text=cam_path, pad=((18,0),(0,0)), size=(50,5), key="CAM_SRC"),
          sg.Button('Connect', pad=((50,0),(0,0))),
          sg.Button('Exit')],
         [sg.Image(size=(1280,720), key="FRAME")]]

window = sg.Window('Cordatus Stream Engine - Camera Player Agent', layout)

while True:  # Event Loop
    event, values = window.read(timeout=interframe_duration)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if is_connected == False and event == 'Connect':
        cse_target = window['TARGET_IP'].get()
        cam_type = window['CAM_TYPE'].get()
        cam_path = window['CAM_SRC'].get()
        token = window['TOKEN'].get()
        client = connect(client, cse_target, cam_type, cam_path, token)
        if client :
            is_connected = True
        time.sleep(1)
    
    if client is None :
        continue

    ret, frame = client.read()
    if ret :
        if is_first :
            is_first = False
        frame = ImageTk.PhotoImage(Image.fromarray(frame))
        window['FRAME'].update(data=frame) 

client.close()
time.sleep(2.0)
window.close()
