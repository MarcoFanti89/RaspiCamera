#!/usr/bin/python
#capture photos, detect differences, upload photos on dropbox

import util
import datetime
import logging

#used to log messages in systemd journal
from systemd.journal import JournalHandler

#------------------------------------------------------------------------------
if __name__ == '__main__':

    log = logging.getLogger('CameraUberwatch')
    log.addHandler(JournalHandler())
    log.setLevel(logging.INFO)

    config = util.read_config()

    last_capture = datetime.datetime.now()

    base_folder = config['Dropbox'].get('base_folder')
    force_capture_seconds = config['Global'].get('force_capture')
    if(force_capture_seconds != None):
        force_capture_seconds = int(force_capture_seconds)
    
    #how much a pixel has to change
    threshold = int(config['Image'].get('threshold'))
    #how many pixels go above threshold to consider image changed
    sensitivity = int(config['Image'].get('sensitivity'))

    #where to save last photo
    filename = config['Global'].get('local_folder') + '/last_capture.jpg'

    image1 = util.captureTestImage()

    while(True):

        try:
            image2 = util.captureTestImage()
            difference = util.compareImages(image1, image2, threshold)

            print('Sensed difference: %d' % difference)
        
            detectedMotion = (difference >= sensitivity)
        
            if(detectedMotion) or ((force_capture_seconds != None and \
                (datetime.datetime.now() - last_capture).total_seconds() > force_capture_seconds)):
            
                subFolder = '/forced_capture/'
                if detectedMotion :
                    log.info('Sensed motion, capturing image...')
                    subFolder = '/motion/'
                else:
                    log.info('Forcing capture after %d seconds idle' % force_capture_seconds)

                util.takeFullPhoto(filename)
                last_capture = datetime.datetime.now()
                destination = base_folder + '/' + util.getDate() + subFolder + util.getTimestamp() + '.jpg'
                util.backup_file(filename, destination)
                log.info('Image sent to dropbox location ' + destination)

            image1 = image2 #ready for next iteration!

        except BaseException as err:
            log.error('Unxepected exception, process dies here. Message: ' + str(err))
            exit(1)

    exit(0)

