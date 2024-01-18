'''
    There should only be ONE of these classes! It is meant to have shared access and has threading protection (using the threadWrapper). 
    This class routs message to every thread in our code. 

    NOTE: This class needs to be pair with the `threading_python_api` in order to work.
'''
# pylint: disable=import-error
from logging_system_display_python_api.graphicsHandler import graphicsHandler
import threading
import time
# pylint: disable=import-error
from threading_python_api.threadWrapper import threadWrapper 

class messageHandler(threadWrapper):
    '''
        This class is the mail man of our code. Any message that needs to be sent to other threads, needs to go through here.
        This class is in charge of send info to the graphics handler (systemEmuo) witch displays it to the user.
        It also is in charge of sending request to unknow threads. 
        For example:
            The systemEmuo does need to know about the matlab_disbacter, but it does want info from it. So it will send a request
                through this class to get that info.
            A data base handler should use this class, because it is handling the data base class it should have direct knowlage 
                of the database. 

            It is completely possible to handle either example with or with out this class, however to maintain a clear code struct 
                here is the rule.

            RULE: IF a class is directly controling another class (A.K.A Do this thing now), do not use the coms class for sending request.
                  If a class is requesting information, or send indrect reqests (A.K.A process this when you have time) it should go through this class.
    '''
    def __init__(self, display_off = False, server_name = ''):
        self.__func_dict = {
            'set_thread_handler' : self.set_thread_handler,
            'send_message_prement' : self.send_message_prement,
            'print_message' : self.print_message,
            'report_thread' : self.report_thread,
            'report_bytes' : self.report_bytes,
            'flush' : self.flush,
            'flush_prem' : self.flush_prem,
            'flush_thread_report' : self.flush_thread_report,
            'flush_bytes' : self.flush_bytes,
            'clear_disp' : self.clear_disp,
            'report_additional_status' : self.clear_disp,
            'report_additional_status' : self.report_additional_status,
            'flush_status' : self.flush_status,
            'run' : self.run,
            'get_system_emuo' : self.get_system_emuo,
            'send_request' : self.send_request,
            'get_return' : self.get_return
        }
        super().__init__(self.__func_dict)
        self.__server_name = server_name
        self.__graphics = graphicsHandler(coms=self, server_name=self.__server_name, display_off=display_off)
        self.__graphics_lock = threading.Lock()
        self.__thread_handler_lock = threading.Lock()
        self.__status_lock = threading.Lock()
        self.__thread_handler = None

    def set_thread_handler(self, threadHandler):
        '''
            This fuction gives the messge handler acces to the threading interface for messages routing.
        '''
        self.__thread_handler = threadHandler
    def send_message_prement(self, message, typeM=2):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.send_message_prement(typeM, message)
    def print_message(self, message, typeM=2):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.send_message(typeM, message)
    def report_thread(self,report):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.report_thread(report)
    def report_bytes(self, byteCount):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.report_byte(byteCount)
    def flush(self):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.write_message_log()
    def flush_prem(self):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.write_message_prement_log()
    def flush_thread_report(self):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.write_thread_report()
    def flush_bytes(self):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.write_byte_report()
    def clear_disp(self):
        # pylint: disable=missing-function-docstring
        with self.__graphics_lock :
            self.__graphics.clear()
    def report_additional_status(self, thread_name, messgae):
        with self.__status_lock :
            self.__graphics.report_additional_status(thread_name, messgae)
    def flush_status(self):
        with self.__status_lock :
            self.__graphics.disp_additional_status()
    def run(self, refresh = 0.5): 
        '''
            This function prints thins in the order we want to see them to the screen.
            NOTE: When debugging it is often useful to comment this function out so the screen 
                doesent get spammed.
        '''
        super().set_status("Running")
        while (super().get_running()):
            self.clear_disp()
            self.flush_prem()
            self.flush_status()
            self.flush_thread_report()
            self.flush()
            self.flush_bytes()
            time.sleep(refresh)
    def get_system_emuo(self):
        # pylint: disable=missing-function-docstring
        return self.__graphics    
    def send_request(self, thread, request):
        '''
            This function is ment to pass information to other threads with out the two threads knowing about each other.
            Bassically the requester say I want to talk to thread x and here is my request. This funct then pass on that requeset. 
            NOTE: threads go by the same name that you see on the display, NOT their class name. This is ment to be easier for the user,
            as they could run the code and see the name they need to send a request to.

            ARGS: 
                thread: The name of the thread as you see it on the gui, or as it is set in main.py
                request: index 0 is the function name, 
                        index 1 to the end is the args for that function.
                NOTE: even if  you are only passing one thing it needs to be a list! 
                    EX: ['funcName']
        '''
        #NOTE: We still need a mutex lock here, even thought the taskHandler is doing locking as well, the taskHandler
        #   pointer (self.__taskHandler) is a varible that needs to be protected.
        with self.__thread_handler_lock:
            temp = self.__thread_handler.pass_request(thread, request)
        return temp
    def get_return(self, thread, requestNum):
        '''
            This function is ment to pass the return values form a thread to another thread, without the threads having explicit knowlage of eachother. 
            ARGS:
                thread: The name of the thread as you see it on the gui, or as it is set in main.py
                requestNum: the number that you got from passReequests, this is basically your ticket to map info back and forth.
        '''
        with self.__thread_handler_lock:
            temp = self.__thread_handler.pass_return(thread, requestNum)
        return temp