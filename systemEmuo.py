'''
    This module is tasked with handling displaying info the the user. 
    For this one is simply prints things to the terminal. 
'''

import time
import threading

class systemEmuo:
    '''
        This systemEmuo prints things to the terminal.
    '''
    def __init__(self, coms = None, display_off =  False):
        self.__messageLock = threading.Lock()
        _ = coms
        self.__display_off = display_off #if this is true we dont display anything

    def print_old_continuos(self, message, delay = 0.15, end=''):
        '''
            This function prints things to there terminal
            ARGS:
                delay: add a delay between each messages
                end: change the lasts thing printed on the line
        '''
        if self.__display_off: 
            return
        if self.__messageLock.acquire(timeout=1):
            print(message, end=end)
            self.__messageLock.release()
        else : 
            raise RuntimeError("Could not aquire message lock")
        if delay != 0:
            time.sleep(delay)
    def clear(self):
        '''
            clears the terminal.
        '''
        if self.__display_off:
            return
        if self.__messageLock.acquire(timeout=1):
            print("\033c", end='') #clears the terminal
            self.__messageLock.release()
        else : 
            raise RuntimeError("Could not aquire message lock")
            