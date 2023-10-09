'''
    This module handles logging and flushing the logs for other classes.
'''

from datetime import datetime
import os

class loggerCustom():
    '''
        This class is meant to handel INDIVIDUAL LOGGING for other classes. 
        It has no threading protection. In other words classes should not 
        share access to one of these objects. 
    '''
    def __init__(self, file):
        try :
            self.__file = open(file, "w+")
        except : # pylint: disable=w0702
            os.mkdir("logs/")
            self.__file = open(file, "w+")# pylint: disable=r1732


    def send_log(self, text):
        # pylint: disable=missing-function-docstring
        self.__file.write(str(datetime.now()) + ": " + text + "\n")
        self.__file.flush()
