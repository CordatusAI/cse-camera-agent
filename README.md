# Cordatus Stream Engine - Camera Player Agent
This sample GUI application aims to provide a foundation for computer vision applications where real time camera streaming is required. It is built on top of CSE Live Stream Agent to benefit from Cordatus Stream Engine's low latency hardware accelerated live camera streaming capabilities for custom AI applications.

Agent is designed and tested to work with local camera sources including USB, CSI and RTSP/HTTP but it can also be used if the remote client necessary ports are forwarded accordingly.

## Test Your Cameras and Cordatus Stream Engine Service
In order to work with physical cameras using this agent, Cordatus Client needs to be up and running on the target device with the source is attached.

For RTSP/HTTP sources, at least one of the main-stream or sub-stream needs to be accessible within the same network. You can test RTSP/HTTP stream availablity by using VLC Media Player prior to this agent.

![RTSP Stream Test Sample](/assets/vlc_hikvision_cam.png)

If Cordatus Client is already running, the Cordatus Stream Engine should be available on port 7005 by default if it is not already occupied by some other application or service.

You can always check the port of the Cordatus Stream Engine service via the following terminal command:
```
ps -ef | grep cordatus_se
```
![Service Port](/assets/cse_port.png)

## 1. Building the Project Locally
Depending on the Python version that your project requires, build the sample image by providing the version information as follows:
```
./build_locally.sh 3.8

or

./build_locally.sh 3.11
```
To run the container:
```
xhost + && docker run -ti --gpus=all --network=host --rm -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY cordatus-camera-player-agent:v1.0-x86-py3.8.19

or

xhost + && docker run -ti --gpus=all --network=host --rm -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY cordatus-camera-player-agent:v1.0-x86-py3.11.9
```

## 2. Get Your Cordatus AI Token
Navigate to the https://cordatus.ai and login to your account. Under the Devices tab, click on the `Actions` button of the target device and select `Generate Token`. This screen will provide you the necessary token information.

![Retrieve your token](/assets/retrieve_token.gif)

## 3. Running the Sample GUI Application

![Run the application](/assets/play_camera.gif)

```
python3 camera_player.py
```

## Custom Code Integration
Defining variables, camera types list, default target and a default HTTP camera source:
```
is_first = True
is_connected = False
cam_types = ['CSI','USB', 'RTSP/HTTP']
cse_target = "http://0.0.0.0:7005"
cam_path = "http://renzo.dyndns.tv/mjpg/video.mjpg"
interframe_duration = 1/33

client:ClientSE = None
```

## Target Device Connection Function
```
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
```

## GUI Elements and Layout
You can customize the application layout as you wish by adding new PySimpleGUI elements inside the layout array. 
```
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
```

### Establishing Connection and Opening the Camera
In order to establish the connection between the local/remote target device and open the camera source, the `connect()` function will be called inside the `while` loop. Then we will be receiving the frames via the `read()` function call inside an infinite `while` loop:
```
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
```