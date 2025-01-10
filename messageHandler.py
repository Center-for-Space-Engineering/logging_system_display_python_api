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
import requests

class messageHandler(threadWrapper):
    '''
        This class is the mail man of our code. Any message that needs to be sent to other threads, needs to go through here.
        This class is in charge of send info to the graphics handler (systemEmuo) witch displays it to the user.
        It also is in charge of sending request to unknown threads. 
        For example:
            The systemEmuo does need to know about the matlab_disaster, but it does want info from it. So it will send a request
                through this class to get that info.
            A data base handler should use this class, because it is handling the data base class it should have direct knowledge 
                of the database. 

            It is completely possible to handle either example with or with out this class, however to maintain a clear code struct 
                here is the rule.

            RULE: IF a class is directly controlling another class (A.K.A Do this thing now), do not use the coms class for sending request.
                  If a class is requesting information, or send indirect requests (A.K.A process this when you have time) it should go through this class.
    '''
    def __init__(self, server_name = '', hostname='127.0.0.1', logging = True, destination:str = 'Local', coms_name:str='coms', display_name:str = 'Local Host'):
        self.__func_dict = {
            'set_thread_handler' : self.set_thread_handler,
            'send_message_permanent' : self.send_message_permanent,
            'print_message' : self.print_message,
            'report_thread' : self.report_thread,
            'report_bytes' : self.report_bytes,
            'flush' : self.flush,
            'flush_prem' : self.flush_prem,
            'flush_thread_report' : self.flush_thread_report,
            'flush_bytes' : self.flush_bytes,
            'report_additional_status' : self.report_additional_status,
            'flush_status' : self.flush_status,
            'run' : self.run,
            'get_system_emuo' : self.get_system_emuo,
            'send_request' : self.send_request,
            'get_return' : self.get_return,
            'set_host_url' : self.set_host_url, 
        }
        super().__init__(self.__func_dict)
        self.__server_name = server_name
        self.__hostName = hostname
        self.__hostName_lock = threading.Lock()
        self.__print_message_lock = threading.Lock()
        self.__permanent_message_lock = threading.Lock()
        self.__report_bytes_lock = threading.Lock()
        self.__report_thread_lock = threading.Lock()
        self.__status_lock = threading.Lock()
        self.__host_url_lock = threading.Lock()
        self.__thread_handler = None
        self.__logging = logging
        self.__destination = destination
        self.__display_name = display_name
        _ = coms_name # not used right now, but here just incase 
        self.__tap_requests = []
        self.__subscriber = []
        self.__host_url = ''
        if self.__destination == "Local": #this is for local reporting
            self.__graphics = graphicsHandler(coms=self, server_name=self.__server_name, mesDisp=20)

    def set_thread_handler(self, threadHandler):
        '''
            This function gives the message handler access to the threading interface for messages routing.
        '''
        self.__thread_handler = threadHandler
    def send_message_permanent(self, message, typeM=2):
        # pylint: disable=missing-function-docstring
        if self.__destination == "Local":
            if self.__permanent_message_lock.acquire(timeout=1): # pylint: disable=R1732
                self.__graphics.send_message_permanent(typeM, message)
                self.__permanent_message_lock.release()
            else :
                raise RuntimeError('Could not aquire permanet message lock')
        else : 
            data = {
                'sender' : self.__hostName,
                'Display_name' : self.__display_name,
                'function' : 'send_message_permanent',
                'message' : message.get_message(), 
                'type' : typeM,
            }

            # Send the POST request
            self.send_post([data])
    def print_message(self, message, typeM=2):
        # pylint: disable=missing-function-docstring
        if self.__destination == "Local":
            if self.__print_message_lock.acquire(timeout=1): # pylint: disable=R1732
                self.__graphics.send_message(typeM, message)
                self.__print_message_lock.release()
            else :
                raise RuntimeError('Could not aquire print message lock')
        else : 
            data = {
                'sender' : self.__hostName,
                'Display_name' : self.__display_name,
                'function' : 'print_message',
                'message' : message.get_message(), 
                'type' : typeM
            }

            # Send the POST request
            self.send_post([data])
    def report_thread(self,report):
        # pylint: disable=missing-function-docstring
        if self.__destination == "Local":
            if self.__report_thread_lock.acquire(timeout=1): # pylint: disable=R1732
                self.__graphics.report_thread(report)
                self.__report_thread_lock.release()
            else :
                raise RuntimeError("Could not aquire report thread lock")
        # I dont want to report thread status on the host
    def report_bytes(self, byteCount):
        # pylint: disable=missing-function-docstring
        if self.__destination == "Local":
            if self.__report_bytes_lock.acquire(timeout=1): # pylint: disable=R1732
                self.__graphics.report_byte(byteCount)
                self.__report_bytes_lock.release()
            else :
                raise RuntimeError("Could not aquire report bytes lock")
        else : 
            data = {
                'sender' : self.__hostName,
                'Display_name' : self.__display_name,
                'message' : byteCount.get_byte_count(), 
                'function' : 'report_bytes',
                'type' : 'report_bytes',
                'time' : byteCount.get_time(),
                'thread_name' : byteCount.get_thread_name()
            }

            # Send the POST request
            self.send_post([data])            
    def report_additional_status(self, thread_name, message):
        # pylint: disable=missing-function-docstring
        if self.__destination == "Local":
            if self.__status_lock.acquire(timeout=1): # pylint: disable=R1732
                self.__graphics.report_additional_status(thread_name, message)
                self.__status_lock.release()
            else :
                raise RuntimeError("Could not aquire status lock")
        else :
            data = {
                'sender' : self.__hostName,
                'Display_name' : self.__display_name,
                'request' : 'report_additional_status',
                'message' : message,
            }

            # Send the POST request
            self.send_post([data])
    def flush(self):
        # pylint: disable=missing-function-docstring
        if self.__print_message_lock.acquire(timeout=1): # pylint: disable=R1732
            self.__graphics.write_message_log()
            self.__print_message_lock.release()
        else :
            raise RuntimeError("Could not aquire print message lock")
    def flush_prem(self):
        # pylint: disable=missing-function-docstring
        if self.__permanent_message_lock.acquire(timeout=1): # pylint: disable=R1732
            self.__graphics.write_message_permanent_log()
            self.__permanent_message_lock.release()
        else :
            raise RuntimeError("Could not aquire permanent message lock")
    def flush_thread_report(self):
        # pylint: disable=missing-function-docstring
        if self.__report_thread_lock.acquire(timeout=1): # pylint: disable=R1732
            self.__graphics.write_thread_report()
            self.__report_thread_lock.release()
        else :
            raise RuntimeError("Could not aquire report thread lock")
    def flush_bytes(self):
        # pylint: disable=missing-function-docstring
        if self.__report_bytes_lock.acquire(timeout=1): # pylint: disable=R1732
            self.__graphics.write_byte_report()
            self.__report_bytes_lock.release()
        else :
            raise RuntimeError("Could not aquire report bytes lock")

    def flush_status(self):
        # pylint: disable=missing-function-docstring
        if self.__status_lock.acquire(timeout=1): # pylint: disable=R1732
            self.__graphics.disp_additional_status()
            self.__status_lock.release()
        else :
            raise RuntimeError("Could not aquire status lock")
    def run(self, refresh = 1): 
        '''
            This function prints thins in the order we want to see them to the screen.
            NOTE: When debugging it is often useful to comment this function out so the screen 
                doest get spammed.
        '''
        super().set_status("Running")
        while (super().get_running()):
            #check to see if there is another task to be done
            request = super().get_next_request()
            # check to see if there is a request
            if request is not None:
                if len(request[1]) > 0:
                    request[3] = self.__function_dict[request[0]](request[1])
                else : 
                    request[3] = self.__function_dict[request[0]]()
                super().complete_request(request[4], request[3])

            if self.__logging and self.__destination == "Local":
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
            This function is to pass information to other threads with out the two threads knowing about each other.
            Basically the requester say I want to talk to thread x and here is my request. This func then pass on that request. 
            NOTE: threads go by the same name that you see on the display, NOT their class name. This is meant to be easier for the user,
            as they could run the code and see the name they need to send a request to.

            ARGS: 
                thread: The name of the thread as you see it on the gui, or as it is set in main.py
                request: index 0 is the function name, 
                        index 1 to the end is the args for that function.
                NOTE: even if  you are only passing one thing it needs to be a list! 
                    EX: ['funcName']
        '''
        #NOTE: We still need a mutex lock here, even thought the taskHandler is doing locking as well, the taskHandler
        #   pointer (self.__taskHandler) is a variable that needs to be protected.

        # NOTE: even if the request is for this class, the task handler will direct it back in to this class so 
        # everything gets passed on. Less efficient, but cleaner code this way. 
        temp = self.__thread_handler.pass_request(thread, request)
        return temp
    def get_return(self, thread, requestNum):
        '''
            This function is meant to pass the return values form a thread to another thread, without the threads having explicit knowledge of each other. 
            ARGS:
                thread: The name of the thread as you see it on the gui, or as it is set in main.py
                requestNum: the number that you got from passRequests, this is basically your ticket to map info back and forth.
        '''
        temp = self.__thread_handler.pass_return(thread, requestNum)
        return temp
    def get_host_name(self):
        '''
            This func returns the host name, so other classes can have access to it. Because the server thread is too busy to be tasked with this function. 
        '''
        if self.__hostName_lock.acquire(timeout=1): # pylint: disable=R1732
            data = self.__hostName
            self.__hostName_lock.release()
        else :
            raise RuntimeError("Could not aquire host name lock")
        return data
    def get_test(self):
        '''
            Tempory function for testing unit tests
        '''
        return "testing"
    def create_tap(self, args):
        '''
            This function creates a tap, a tap will send the data it receives from the serial line to the class that created the tap.
            ARGS:
                args[0] : tap function to call. 
                args[1] :  name of subscriber
        '''
        self.__tap_requests.append(args[0])
        self.__subscriber.append(args[1])
    def set_host_url(self, args):
        '''
            The server calls this function to set the host url, so coms can report to the host server.

            Args :
                args[0] : host url.
        '''
        print(f'set url {args[0]}')
        if self.__host_url_lock.acquire(timeout=1): # pylint: disable=R1732
            self.__host_url = args[0]
            self.__host_url_lock.release()
        else :
            raise RuntimeError("Could not aquire host url lock")

    def send_post(self, args):
        '''
            Send a post request to the host server for logging

            ARGS:
                args[0] : dictionary of data to send
        '''
        data = args[0]
        request = 'NA'

        if len(args) > 1:
            request = args[1]
    
        if self.__host_url_lock.acquire(timeout=1): # pylint: disable=R1732
            temp_url = self.__host_url
            self.__host_url_lock.release()
        else :
            raise RuntimeError("Could not aquire host url lock")
        
        response = None

        try :
            if temp_url != '': #If the host url hasn't been set yet then we are not going to send logs. 
                # Send the POST request
                if request == 'NA':
                    response = requests.post('http://' + temp_url + '/logger_reports', data=data, timeout=1)
                else :
                    response = requests.post('http://' + temp_url + request, json=data, timeout=1)

                # Check the response
                if response.status_code != 200:
                    print(f'POST request to {temp_url} failed with status code: {response.status_code}')
        except Exception as e: # pylint: disable=W0702
            #if request fails just move on
            pass
        return response
