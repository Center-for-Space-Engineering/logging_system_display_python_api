'''
    This module is tasked with formatting all the messages that will be displayed
    by system emuo, it also stores all logs, and sends them to location that need the logging information, like the server.  
'''
import datetime

# pylint: disable=import-error

#import DTO for communicating internally
from logging_system_display_python_api.DTOs.logger_dto import logger_dto
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto #pylint: disable=w0611
from logging_system_display_python_api.logger import loggerCustom

class graphicsHandler():
    '''
        This module is tasked with distributing all the log message to the server. 
    '''
    def __init__(self, mesDisp = 10, byte_disp = 10, coms = None, server_name = ''):
        self.__messages = [(2, logger_dto(time = f"{datetime.datetime.now()}", message = 'Graphics handler started'))]
        self.__threads_status = []
        self.__message_displayed = mesDisp
        self.__byte_report = []
        self.__byte_report_server = {}
        self.__byte_disp = byte_disp
        self.__messages_permanent = []
        self.__coms = coms
        self.__status_message = {}
        self.__server_name = server_name
        # self.__logger = loggerCustom("logs/graphicsHandler.txt")

    def write_message_log(self):
        # pylint: disable=missing-function-docstring
        messages = []
        for num in self.__messages:
            messages.append(num[1])
        self.__coms.send_request(self.__server_name, ['write_message_log', messages]) #send the server the info to display

    def send_message(self, num, message):
        # pylint: disable=missing-function-docstring
        dto = logger_dto(time=str(datetime.datetime.now()), message=message.get_message())
        self.__messages.append((num, dto))
        if len(self.__messages) >= self.__message_displayed: # this basically makes it a FIFO queue for messaging
            self.__messages.remove(self.__messages[0])
        # self.__logger.send_log(f"leng messages: {len(self.__messages)}")
    
    def write_message_permanent_log(self):
        # pylint: disable=missing-function-docstring
        messages =[]
        for num in self.__messages_permanent:
            messages.append(num[1])
        self.__coms.send_request(self.__server_name, ['write_prem_message_log', messages]) #send the server the info to display

    def send_message_permanent(self, message_type, dto):
        # pylint: disable=missing-function-docstring
        self.__messages_permanent.append((message_type, dto))
    
    def report_thread(self,report):
        # pylint: disable=missing-function-docstring
        self.__threads_status = report

    def write_thread_report(self):
        # pylint: disable=missing-function-docstring
        report_copy = self.__threads_status.copy() #python is pass by reference so if we pass this to another thread, and then clear it, the data will be lost. So we make a copy
        self.__coms.send_request(self.__server_name, ['thread_report', report_copy]) #send the server the info to display
        if len(self.__threads_status) != 0:
            self.__threads_status.clear()
        # self.__logger.send_log(f"leng thread report: {len(self.__threads_status)}")

    def write_byte_report(self):
        # pylint: disable=missing-function-docstring
        self.__coms.send_request(self.__server_name, ['report_byte_status', self.__byte_report_server]) #send the server the info to display

    def report_byte(self, byte_report):
        # pylint: disable=missing-function-docstring
        self.__byte_report.append(str(byte_report))
        thread_name = byte_report.get_thread_name()
        if thread_name in self.__byte_report_server:
            self.__byte_report_server[thread_name].append({
                'time' : byte_report.get_time(),
                'bytes': byte_report.get_byte_count()
            })
        else :
            self.__byte_report_server[thread_name] = [{
                'time' : byte_report.get_time(),
                'bytes': byte_report.get_byte_count()
            }]
        if len(self.__byte_report) >= self.__byte_disp : # this basically makes it a FIFO queue
            self.__byte_report.remove(self.__byte_report[0])
        # self.__logger.send_log(f"leng report bytes: {len(self.__byte_report)}")

    def report_additional_status(self, thread_name, message):
        # pylint: disable=missing-function-docstring
        self.__status_message[thread_name] = message
    
    def disp_additional_status(self):
        # pylint: disable=missing-function-docstring
        self.__coms.send_request(self.__server_name, ['report_status', self.__status_message]) #send the server the info to display
