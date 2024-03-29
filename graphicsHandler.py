'''
    This module is tasked with formatting all the messages that will be displayed
    by system emuo, it also stores all logs, and sends them to location that need the logging information, like the server.  
'''
import datetime
from termcolor import colored
# pylint: disable=import-error
from logging_system_display_python_api.systemEmuo import systemEmuo as sys

#import DTO for communicating internally
from logging_system_display_python_api.DTOs.logger_dto import logger_dto
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto #pylint: disable=w0611

class graphicsHandler(sys):
    '''
        This module is tasked with formatting all the messages that will be displayed
        by system emuo.

        Serval encodings can be sent here the are:

        0  : 'red' : Error
        1  : 'magenta' : warning
        2  : 'blue' : Log 
        3  : 'green' : get request
        4  : 'cyan' : data type found
        5  : 'yellow' : Sensor connected
        6  : 'light_cyan' : thread created
        7  : 'white' : info
        8  : 'light_magenta' : Command Mapped
        9  : 'light_blue' : reserved
    '''
    def __init__(self, mesDisp = 10, byte_disp = 10, byte_div = 100, coms = None, server_name = '', display_off=False):
        self.__colors = ['red', 'magenta', 'blue', 'green', 'cyan', 'yellow', 'light_cyan', 'white', 'light_magenta', 'light_blue']
        self.__types = ['Error: ', 'Warning: ', 'Log: ', 'Get request: ', 'Data type found: ', 'Sensor connected: ', 'Thread created: ', 'Info: ', 'Command Mapped: ', 'reserved: ']
        self.__messages = [(2, logger_dto(time = f"{datetime.datetime.now()}", message = 'Graphics handler started'))]
        self.__threads_status = []
        self.__message_displayed = mesDisp
        self.__byte_report = []
        self.__byte_report_server = {}
        self.__byte_disp = byte_disp
        self.__byte_div = byte_div
        self.__messages_permanent = []
        self.__coms = coms
        self.__status_message = {}
        self.__server_name = server_name
        super().__init__(self.__coms, display_off=display_off)

    def write_message_log(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Logs report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        messages = []
        for num in self.__messages:
            super().print_old_continuos(colored(self.__types[num[0]], self.__colors[num[0]]) + str(num[1]), delay=0, end='\n')
            messages.append(num[1])
        self.__coms.send_request(self.__server_name, ['write_message_log', messages]) #send the server the info to display
        super().print_old_continuos("\n")

    def send_message(self, num, message):
        # pylint: disable=missing-function-docstring
        dto = logger_dto(time=str(datetime.datetime.now()), message=message.get_message())
        self.__messages.append((num, dto))
        if len(self.__messages) >= self.__message_displayed: # this basically makes it a FIFO queue for messaging
            self.__messages.remove(self.__messages[0])
    
    def write_message_permanent_log(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Permanent Log report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        messages =[]
        for num in self.__messages_permanent:
            super().print_old_continuos(colored(self.__types[num[0]],self.__colors[num[0]]) + str(num[1]), delay=0, end='\n')
            messages.append(num[1])
        self.__coms.send_request(self.__server_name, ['write_prem_message_log', messages]) #send the server the info to display
        super().print_old_continuos("\n")

    def send_message_permanent(self, message_type, dto):
        # pylint: disable=missing-function-docstring
        self.__messages_permanent.append((message_type, dto))
    
    def report_thread(self,report):
        # pylint: disable=missing-function-docstring
        self.__threads_status = report

    def write_thread_report(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Thread report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for report in self.__threads_status:
            if report[2] == "Running":
                super().print_old_continuos("["+colored(report[1].get_time(), self.__colors[2]) + f"] Thread {report[0]}: " + colored(report[1].get_message(),self.__colors[3]) + "\t", delay=0)
            elif report[2] == "Error":
                super().print_old_continuos(colored(report[2], self.__colors[0]) + f" Thread {report[0]}: " + colored(report[1].get_message(),self.__colors[0])+ "\t", delay=0)
            else :
                super().print_old_continuos("[" + colored(report[1].get_time(), self.__colors[2]) + "]\t" + f"] Thread {report[0]}: " + colored(report[1].get_message(),self.__colors[2])+ "\t", delay=0)
        report_copy = self.__threads_status.copy() #python is pass by reference so if we pass this to another thread, and then clear it, the data will be lost. So we make a copy
        self.__coms.send_request(self.__server_name, ['thread_report', report_copy]) #send the server the info to display
        if len(self.__threads_status) != 0:
            self.__threads_status.clear()
            super().print_old_continuos("\n") # print new line
        super().print_old_continuos("\n")

    def write_byte_report(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Byte report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for  report in self.__byte_report:
            super().print_old_continuos(report, end='\n', delay=0)
        super().print_old_continuos(colored("KEY : ", 'light_blue') + colored(('\u25a0'), 'magenta') + f"= {self.__byte_div} bytes.", end='\n', delay=0)
        super().print_old_continuos("\n")

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
        self.__coms.send_request(self.__server_name, ['report_byte_status', self.__byte_report_server]) #send the server the info to display

    def report_additional_status(self, thread_name, message):
        # pylint: disable=missing-function-docstring
        self.__status_message[thread_name] = message
    
    def disp_additional_status(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Status report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for thread_name in self.__status_message: #pylint: disable=c0206
            super().print_old_continuos(colored(f'Report: {thread_name}', 'magenta') + str(self.__status_message[thread_name]), delay=0, end='\n')

        self.__coms.send_request(self.__server_name, ['report_status', self.__status_message]) #send the server the info to display
        super().print_old_continuos("\n")
