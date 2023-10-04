import random
import datetime
from logging_system_display_python_api.systemEmuo import systemEmuo as sys 
# from systemEmuo import systemEmuo as sys #for running by its self




class graphicsHandler(sys):
    '''
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
    def __init__(self, mesDisp = 10, coms = None):

        self.__colors = ['red', 'magenta', 'blue', 'green', 'cyan', 'yellow', 'light_cyan', 'white', 'light_magenta', 'light_blue']
        self.__types = ['Error: ', 'Warning: ', 'Log: ', 'Get request: ', 'Data type found: ', 'Sensor connected: ', 'Thread created: ', 'Info: ', 'Command Mapped: ', 'reserved: ']
        self.__messages = [(2, f"[{datetime.datetime.now()}]" + ' Graphics handler started')]
        self.__threaedsStatus = []
        self.__messagsDisplayed = mesDisp
        self.__messagesPrement = []
        self.__coms = coms
        super().__init__(self.__coms) 

    def test(self):
        self.sendMessage(0, "Error") 
        self.sendMessage(1, "not a real warning") 
        self.sendMessage(2, "nice color ") 
        print("Done queing messages:")
        self.writeMessageLog()

    def writeMessageLog(self):
        for num in self.__messages:
            super().print_old_continuos(num[1])
    
    def sendMessage(self, num, message):
        self.__messages.append((num, f"[{datetime.datetime.now()}]" + message))
        if len(self.__messages) >= self.__messagsDisplayed : # this basically makes it a FIFO queue for messaging
            self.__messages.remove(self.__messages[0])
    
    def sendMessagePrement(self, num, message):
        self.__messagesPrement.append((num, f"[{datetime.datetime.now()}]" + message))
    
    def writeMessagePrementLog(self):
        for num in self.__messagesPrement:
            super().print_old_continuos(num[1], key='-PRELOGS-')

    def reportThread(self,report):
        self.__threaedsStatus = report

    def writeThreadReport(self):
        for report in self.__threaedsStatus:
            if report[1] == "Running":
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + report[1], key='-THREADS-')
            elif report[1] == "Error":
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + report[1], key='-THREADS-')
            else :
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + report[1], key='-THREADS-')
        if(len(self.__threaedsStatus) != 0):
            self.__threaedsStatus.clear()
    
    #We dont need this function but the messages handler needs them so we are gonna write dummy functions
    def reportByte(self, byteCount):
        pass
    def writeByteReport(self):
        pass