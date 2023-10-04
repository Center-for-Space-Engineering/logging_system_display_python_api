'''
    This module is tasked with formatting all the messages that will be dispalyed
    by system emulo.
'''
import datetime
# pylint: disable=import-error
from logging_system_display_python_api.systemEmuo import systemEmuo as sys 
# from systemEmuo import systemEmuo as sys #for running by its self

class graphicsHandler(sys):
    '''
        This module is tasked with formatting all the messages that will be dispalyed
        by system emulo.
    '''
    def __init__(self, mesDisp = 10, coms = None):
        self.__messages = [(2, f"[{datetime.datetime.now()}]" + ' Graphics handler started')]
        self.__threaeds_status = []
        self.__messags_displayed = mesDisp
        self.__messages_prement = []
        self.__coms = coms
        super().__init__(self.__coms) 

    def write_message_log(self):
        # pylint: disable=missing-function-docstring
        for num in self.__messages:
            super().print_old_continuos(num[1])
    
    def send_message(self, num, message):
        # pylint: disable=missing-function-docstring
        self.__messages.append((num, f"[{datetime.datetime.now()}]" + message))
        if len(self.__messages) >= self.__messags_displayed : # this basically makes it a FIFO queue for messaging
            self.__messages.remove(self.__messages[0])
    
    def send_message_prement(self, num, message):
        # pylint: disable=missing-function-docstring
        self.__messages_prement.append((num, f"[{datetime.datetime.now()}]" + message))
    
    def write_message_prement_log(self):
        # pylint: disable=missing-function-docstring
        for num in self.__messages_prement:
            super().print_old_continuos(num[1], key='-PRELOGS-')

    def report_thread(self,report):
        # pylint: disable=missing-function-docstring
        self.__threaeds_status = report

    def write_thread_report(self):
        # pylint: disable=missing-function-docstring
        for report in self.__threaeds_status:
            if report[1] == "Running":
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + report[1], key='-THREADS-')
            elif report[1] == "Error":
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + report[1], key='-THREADS-')
            else :
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + report[1], key='-THREADS-')
        if len(self.__threaeds_status) != 0:
            self.__threaeds_status.clear()
    
    #We dont need this function but the messages handler needs them so we are gonna write dummy functions
    def report_byte(self, _):
        # pylint: disable=missing-function-docstring
        pass
    def write_byte_report(self):
        # pylint: disable=missing-function-docstring
        pass
