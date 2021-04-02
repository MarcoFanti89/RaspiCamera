import os
import sys
import configparser
import requests
import pathlib
import dropbox
import subprocess
import traceback

from datetime import datetime
from PIL import Image
from dropbox.files import WriteMode

#read configuration file
def read_config():

    #config file in same directory of this source
    config_file = str(pathlib.Path(__file__).parent.absolute()) + '/config.properties'

    if os.path.exists(config_file) :
        config = configparser.RawConfigParser()
        config.read(config_file)        
        return config

# Capture a small test image (for motion detection)
#returns pixel data in PixelAccess obj type
def captureTestImage():
##    
    print('Capturing test image')
    try:
        config = read_config()
        temp_file = config['Global'].get('local_folder') + '/temp.bmp'
        command = "/opt/vc/bin/raspistill -w %s -h %s -e bmp -o %s" % (100, 75, temp_file)

        print('Executing command ' + command)
        
        #imageData.write(subprocess.check_output(command, shell=True))
        subprocess.run(command, check=True, shell=True)
        
        im = Image.open(temp_file)
        pixelData = im.load()
        return pixelData

    except BaseException as err:
        print('Error getting photo: ' + str(err))
        traceback.print_exc()
        return None
    

#returns how many pixels differs more than the threshold
def compareImages(pixel_one, pixel_two, threshold):
    changedPixels = 0
    
    for x in range(0, 100):
        for y in range(0, 75):
            # adds channels r(0), g(1), b(2) #TO_REVIEW: maybe only 1 channel is already ok. People say green
            pixdiff = abs(pixel_one[x,y][0] - pixel_two[x,y][0]) + \
                      abs(pixel_one[x,y][1] - pixel_two[x,y][1]) + \
                      abs(pixel_one[x,y][2] - pixel_two[x,y][2])
            if pixdiff > threshold:
                changedPixels += 1

    return changedPixels


# Capture a full size image, save to disk in specified location
def takeFullPhoto(path):
    config = read_config()
    height = config['Image'].get('height')
    width = config['Image'].get('width')
    quality = config['Image'].get('quality')

    subprocess.call("/opt/vc/bin/raspistill -w %s -h %s -e jpg -q %s -t 500 -o %s" % \
                    (width, height, quality, path), shell=True)
    print('Captured full resolution photo')
    return path
    

#return access token that can be used in calls to dropbox api
def getDropBoxAccessToken():
    config = read_config()

    formData = 'refresh_token=' + config['Dropbox'].get('refresh_token') +\
        '&grant_type=refresh_token' +\
        '&client_id=' + config['Dropbox'].get('client_id') +\
        '&client_secret=' + config['Dropbox'].get('client_secret')

    try:
        response = requests.post(
            'https://api.dropboxapi.com/oauth2/token',
            headers={'Content-Type' : 'application/x-www-form-urlencoded'},
            data=formData
        )
    except BaseException as http_err:
        print('HTTP error occurred: ' + str(http_err)) # + str(http_err))
        exit(1)

    if response.status_code != 200 :
        print('Dropbox authentication failed error ' + str(response.status_code) + \
                '\nReturned: ' + str(response.content))
        exit(2)

    access_token = response.json().get('access_token');

    return access_token

#perform file backup
#source = local file
#destination = dropbox location
def backup_file(source, destination):

    accessToken = getDropBoxAccessToken()
    dbox = dropbox.Dropbox(accessToken)

    try:
        dbox.users_get_current_account()
    except BaseException as err:
        print('Invalid access token ' + str(err))
        return('Invalid token error: ' + str(err))

    with open(source, 'rb') as f:
        print('Uploading file to Dropbox location: ' + destination)

        try:
            dbox.files_upload(f.read(), destination, mode=WriteMode('overwrite'))

            print('File copied successfully')    
            return('OK')
            
        except BaseException as err:
            print(err)
            return(str(err))

def getTimestamp():
    now = datetime.now()
    timestamp = '%04d_%02d_%02d-%02d:%02d:%02d' % \
                (now.year, now.month, now.day, \
                 now.hour, now.minute, now.second)
    return timestamp

def getDate():
    today = datetime.today()
    todayStr = '%04d_%02d_%02d' % \
                (today.year, today.month, today.day)
    return todayStr
