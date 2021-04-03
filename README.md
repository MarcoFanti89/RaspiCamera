# Raspberry PI surveillance camera

This python script monitors the raspberry camera, captures a photo when a change is detected and uploads it to Dropbox

## Configuration
All the configuration is in the file `config.properties`, example here:

```
[Global]
;where to save temp files created by software
;only 2 images file will be stored it at any time
;I suggest to use a ramdisk
local_folder=/home/user/ramdisk

;force an image capture every X seconds also when no motion is detected
force_capture=600

[Image]
;Image quality from 1 to 100
quality=80
width=1024
height=768

;Threshold (how much a pixel has to change to be marked as "changed")
;(every pixel has 3 channels -rgb- each one 0-255)
threshold=30

;Sensitivity (how many changed pixels before capturing an image)
sensitivity=70

[Dropbox]
;read all README file to know how to get these dropbox parameters
refresh_token=<REFRESH_TOKEN>
client_id=<APP_KEY>
client_secret=<APP_SECRET>
;will save files under this dropbox folder (must start with a '/')
base_folder=/raspi_camera
```

## Run the script

To run this script, execute `RaspiCamera.py`

These is also a utility script which you can use to backup a local file to your dropbox, look at `./copyToDropbox.py --help`

### Configure as daemon to run at startup
Create a new systemd service file `/etc/systemd/system/raspicamera.service`
```
[Service]
Type=simple
ExecStart=/path/to/RaspiCamera.py

;if service crashes for any reason, restart it after 30 seconds
Restart=always
RestartSec=30

[Unit]
Requires=multi-user.target
After=multi-user.target

[Install]
WantedBy=multi-user.target
```
Enable execution at raspberry statup with `systemctl enable raspicamera` 

## Provide access to your dropbox to the script
You need to create your own Dropbox app, to generate a token that this script will use to login on your Dropbox account

### Create the Dropbox app
Go on https://www.dropbox.com/developers/apps and create your own app.
In the permission tab, give the permissions to write files and folders.

Note down the `App key` and the `App secret`, are necessary in the following steps

### Get dropbox auth code
In a web browser, visit the page `https://www.dropbox.com/1/oauth2/authorize?client_id=<APP_KEY>&response_type=code&token_access_type=offline` where `<APP_KEY>` is the one you got in the previous step.

In the web page you will perform the login to your dropbox account, at the end you will receive an Authorization code, note it down for the next step

### Get dropbox refresh token
The refresh token is what the python script will use to authenticate on dropbox.

URL = `https://api.dropboxapi.com/oauth2/token`
Method = `POST`

example with curl:
```
curl https://api.dropbox.com/oauth2/token \
    -d code=<AUTHORIZATION_CODE> \
    -d grant_type=authorization_code \
    -d client_id=<APP_KEY> \
    -d client_secret=<APP_SECRET>
```

Answer is a JSON from which you only need the `refresh_token`

