#!/usr/bin/python
#utility executable from command line to copy files from local computer to dropbox
# use: pass parameters --source=SOURCE_FILE --destination DROPBOX_LOCATION

import sys
import getopt
import util

def print_help():
    print('Usage: copyToDropbox.py -s LOCAL_FILE -d DROPBOX_LOCATION')
    print('   Or: copyToDropbox.py --source=LOCAL_FILE --destination DROPBOX_LOCATION')
    print('   Or: copyToDropbox.py --help')
    exit(0)

#read command line parameters, ensure they are ok
def read_command_line():
    short_options = 's:d:h'
    long_options = [ 'source=', 'destination=', 'help' ]

    source = None
    destination = None
    error = False

    try:
        arguments_list = sys.argv[1:] #all but first
        arguments, values = getopt.getopt(arguments_list, short_options, long_options)

        for current_arg, current_value in arguments:
            if current_arg in ('-s', '--source'):
                source = current_value
            elif current_arg in ('-d', '--destination'):
                destination = current_value
            elif current_arg in ('-h', '--help'):
                print_help()

        if(source == None):
            print('Missing mandatory parameter --source')
            error = True
        if(destination == None):
            print('Missing mandatory parameter --destination')
            error = True

        if error:
            exit(1)

        return source, destination

    except getopt.error as err:
        print('Error parsing command line parameters %s' % (str(err)))
        exit(1)

#------------------------------------------------------------------------------
if __name__ == '__main__':

    source, destination = read_command_line()

    try:
        util.backup_file(source, destination)
    except BaseException as err:
        print('Impossible to backup file to Dropbpx. Error: ' + str(err))

    exit(0)


