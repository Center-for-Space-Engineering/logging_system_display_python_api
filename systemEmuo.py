import time
from termcolor import colored, cprint
import PySimpleGUI as sg
from threading_python_api.threadWrapper import threadWrapper # running from server
import os.path
import threading

'''
    This class is used for displaying information. This allows for it to be changed for different implemenations 
    with out having to change all the intral plumming of the information. 
'''
class systemEmuo(threadWrapper):
    def __init__(self, coms = None):
        super().__init__()
        self.__messageLock = threading.Lock()
        self.__coms = coms
        self.__matLabCodeRequstNum = -1
        self.__avaibleMatlab = None
        self.__messageMap = {
            '-PRELOGS-' : [],
            '-THREADS-' : [],
            '-LOGS-' : [],
        }
        self.__file_list_column = [
            [
            sg.Text("Find MatLab code:"),
            sg.In(size=(40, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
            ],
            [
                sg.Listbox(
                    values=[], enable_events=True, size=(80, 10), key="-FILE LIST-"
                )
            ],
            [sg.Text("Avaible MatLab code:")],
            [sg.Listbox(size=(80, 10), enable_events=True,  key="-MATCODE-", values=[])],
        ]
        self.__logs_viewer_column = [
            [sg.Text("Permanent Log report:")],
            [sg.Listbox(size=(80, 10), enable_events=True,  key="-PRELOGS-", values=[], no_scrollbar=True)],
            [sg.Text("Threading report:")],
            [sg.Listbox(size=(80, 10), enable_events=True,  key="-THREADS-", values=[], no_scrollbar=True)],
            [sg.Text("Log report:")],
            [sg.Listbox(size=(80, 10), enable_events=True,  key="-LOGS-", values=[], no_scrollbar=True)],
        ]

        self.__processing_flow_viewer =[
            [sg.Listbox(size=(160, 10), enable_events=True,  key="-PROCESS-", values=[])],
        ]
        
        # ----- Full layout -----
        self.__layout = [
            [
                [sg.Column(self.__file_list_column, element_justification='t'),
                sg.VSeperator(),
                sg.Column(self.__logs_viewer_column),
                ],
                sg.Frame("Processing Flow", self.__processing_flow_viewer, title_color='blue', key="-PROCESS-"),
            ]

        ]
        self.__window = sg.Window("CSE Ground", self.__layout)

    def print_old_continuos(self, message, key = '-LOGS-'):
        with self.__messageLock:
            self.__messageMap[key].append(message)
    
    def clear(self):
        with self.__messageLock:
            for item in self.__messageMap:
                self.__messageMap[item].clear()
    
    def run(self):
        super().setStatus("Running")
        while True:
            event, values = self.__window.read(timeout=20)
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == sg.TIMEOUT_EVENT:
                with self.__messageLock:
                    for item in self.__messageMap:
                        self.__window[item].update(self.__messageMap[item])
                #dont need mutex locking here because this thread is the onlything that can touch this internal data
                if(self.__matLabCodeRequstNum == -1): #check to see if we have sent the request
                    self.__matLabCodeRequstNum  = self.__coms.sendRequest('Matlab Disbatcher', ['getMappingsList'])
                else : #if we have check to see if there is a return value
                    self.__avaibleMatlab = self.__coms.getReturn('Matlab Disbatcher', self.__matLabCodeRequstNum)
                if(self.__avaibleMatlab != None): # if the return time is not none then we update the code
                    self.__window['-MATCODE-'].update(self.__avaibleMatlab[0])
                    self.__window['-PROCESS-'].update(self.__avaibleMatlab[1])
                    #reset for next pass now
                    self.__avaibleMatlab = None
                    self.__matLabCodeRequstNum = -1

            # Folder name was filled in, make a list of files in the folder
            if event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    # Get list of files in folder
                    file_list = os.listdir(folder)
                except:
                    file_list = []
                print(f"File list: {file_list}")
                fnames = [
                    f
                    for f in file_list
                    if os.path.isfile(os.path.join(folder, f))
                    and f.lower().endswith((".m"))
                ]
                self.__window["-FILE LIST-"].update(fnames)
            elif event == "-FILE LIST-":  # A file was chosen from the listbox
                try:
                    pass #TODO: make this create processing chains
                except:
                    pass
            elif event == "-MATCODE-":
                func = values["-MATCODE-"][0]
                self.__matLabCodeRequstNum  = self.__coms.sendRequest('Matlab Disbatcher', ['dispatchFuntion', func])


        super().setStatus("Complete")
        self.__window.close()