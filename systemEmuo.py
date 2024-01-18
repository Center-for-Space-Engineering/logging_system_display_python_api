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
            This function prints things to ther termal
            ARGS:
                delay: add a delay between each messages
                end: cheange the lasst thing printed on the line
        '''
        if self.__display_off: return
        with self.__messageLock:
            print(message, end=end)
            if delay != 0:
                time.sleep(delay)
    def clear(self):
        '''
            clears the termal.
        '''
        if self.__display_off: return
        with self.__messageLock:
            print("\033c", end='') #clears the terminal
            