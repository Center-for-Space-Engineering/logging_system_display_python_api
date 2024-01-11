'''
    This module is tasked with formatting all the messages that will be dispalyed
    by system emulo.
'''
import datetime
from termcolor import colored
# pylint: disable=import-error
from logging_system_display_python_api.systemEmuo import systemEmuo as sys 


class graphicsHandler(sys):
    '''
        This module is tasked with formatting all the messages that will be dispalyed
        by system emulo.

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
    def __init__(self, mesDisp = 10, byte_disp = 10, byte_div = 100, coms = None, server_name = ''):
        self.__colors = ['red', 'magenta', 'blue', 'green', 'cyan', 'yellow', 'light_cyan', 'white', 'light_magenta', 'light_blue']
        self.__types = ['Error: ', 'Warning: ', 'Log: ', 'Get request: ', 'Data type found: ', 'Sensor connected: ', 'Thread created: ', 'Info: ', 'Command Mapped: ', 'reserved: ']
        self.__messages = [(2, colored(f"[{datetime.datetime.now()}]", 'light_blue') + '\tGraphics handler started')]
        self.__threaeds_status = []
        self.__messags_displayed = mesDisp
        self.__byte_report = []
        self.__byte_disp = byte_disp
        self.__byte_div = byte_div
        self.__messages_prement = []
        self.__coms = coms
        self.__status_message = {}
        self.__server_name = server_name
        super().__init__(self.__coms)

    def write_message_log(self):
        # pylint: disable=missing-function-docstring
        # super().print_old_continuos(colored('Loggs report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        messages = ['Logging Report:\n']
        for num in self.__messages:
            # super().print_old_continuos(colored(self.__types[num[0]],self.__colors[num[0]]) + num[1], delay=0, end='\n')
            messages.append(num[1])
        self.__coms.send_request(self.__server_name, ['write_message_log', messages]) #send the server the info to display
        # print()

    def send_message(self, num, message):
        # pylint: disable=missing-function-docstring
        self.__messages.append((num, colored(f"[{datetime.datetime.now()}]", 'light_blue') + "\t" + message))
        if len(self.__messages) >= self.__messags_displayed : # this basically makes it a FIFO queue for messaging
            self.__messages.remove(self.__messages[0])
    
    def send_message_prement(self, num, message):
        # pylint: disable=missing-function-docstring
        self.__messages_prement.append((num, colored(f"[{datetime.datetime.now()}]", 'light_blue') + "\t" + message))
    
    def write_message_prement_log(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Permanent Log report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for num in self.__messages_prement:
            super().print_old_continuos(colored(self.__types[num[0]],self.__colors[num[0]]) + num[1], delay=0, end='\n')
        print()

    def report_thread(self,report):
        # pylint: disable=missing-function-docstring
        self.__threaeds_status = report

    def write_thread_report(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Thread report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for report in self.__threaeds_status:
            if report[1] == "Running":
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + colored(report[1],self.__colors[3]) + "\t", delay=0)
            elif report[1] == "Error":
                super().print_old_continuos(f"{report[2]} Thread {report[0]}: " + colored(report[1],self.__colors[0])+ "\t", delay=0)
            else :
                super().print_old_continuos(f"{report[2]} Thread {report[0]}: " + colored(report[1],self.__colors[2])+ "\t", delay=0)
        if len(self.__threaeds_status) != 0:
            self.__threaeds_status.clear()
            print() # print new line
        print()

    def write_byte_report(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Byte report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for  report in self.__byte_report:
            super().print_old_continuos(report, end='\n', delay=0)
        super().print_old_continuos(colored("KEY : ", 'light_blue') + colored((u'\u25a0'), 'magenta') + f"= {self.__byte_div} bytes.", end='\n', delay=0)
        print()

    def report_byte(self, numbytes):
        # pylint: disable=missing-function-docstring
        bytesOriganal = numbytes
        numbytes //= self.__byte_div
        self.__byte_report.append(colored(f"Bytes received at: [{datetime.datetime.now()}]", 'light_blue') + " |" + colored((u'\u25a0' * numbytes) + f"({bytesOriganal})", 'magenta'))
        if len(self.__byte_report) >= self.__byte_disp : # this basically makes it a FIFO queue for messaging
            self.__byte_report.remove(self.__byte_report[0])

    def report_additional_status(self, thread_name, message):
        # pylint: disable=missing-function-docstring
        self.__status_message[thread_name] = message
    
    def disp_additional_status(self):
        # pylint: disable=missing-function-docstring
        super().print_old_continuos(colored('Status report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for thread_name in self.__status_message:
            super().print_old_continuos(colored(f'Report: {thread_name}', 'magenta') + self.__status_message[thread_name], delay=0, end='\n')
        print()
