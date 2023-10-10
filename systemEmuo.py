'''
    This modules handels displaying information to the user.
    In this case it is a gui.
    NOTE: There should only be one system emuo. 
'''

import PySimpleGUI as sg
# pylint: disable=import-error
from threading_python_api.threadWrapper import threadWrapper
import os.path
import threading


class systemEmuo(threadWrapper):
    '''
        This class is used for displaying information. This allows for it to be changed for different implemenations 
        with out having to change all the intral plumming of the information. 
    '''
    def __init__(self, coms = None):
        super().__init__()
        self.__message_lock = threading.Lock()
        self.__coms = coms
        self.__mat_lab_code_requst_num = -1
        self.__avaible_matlab = None
        self.__message_map = {
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
        # pylint: disable=missing-function-docstring
        with self.__message_lock:
            self.__message_map[key].append(message)
    def clear(self):
        # pylint: disable=missing-function-docstring
        with self.__message_lock:
            for item in self.__message_map: #pylint: disable=C0206
                self.__message_map[item].clear()   
    def run(self):
        '''
            This function handles running the gui, it looks for input,
            then updates the display.
        '''
        super().set_status("Running")
        while True:
            event, values = self.__window.read(timeout=20)
            if event == "Exit" or event == sg.WIN_CLOSED: #pylint: disable=R1714
                break
            if event == sg.TIMEOUT_EVENT:
                with self.__message_lock:
                    for item in self.__message_map: #pylint: disable=C0206
                        self.__window[item].update(self.__message_map[item])
                #dont need mutex locking here because this thread is the onlything that can touch this internal data
                #check to see if we have sent the request
                if self.__mat_lab_code_requst_num == -1: 
                    self.__mat_lab_code_requst_num  = self.__coms.send_request('Matlab Disbatcher', ['get_mappings_list'])
                else : #if we have check to see if there is a return value
                    self.__avaible_matlab = self.__coms.get_return('Matlab Disbatcher', self.__mat_lab_code_requst_num)
                if self.__avaible_matlab is not None: 
                    # if the return time is not none then we update the code
                    self.__window['-MATCODE-'].update(self.__avaible_matlab[0])
                    self.__window['-PROCESS-'].update(self.__avaible_matlab[1])
                    #reset for next pass now
                    self.__avaible_matlab = None
                    self.__mat_lab_code_requst_num = -1

            # Folder name was filled in, make a list of files in the folder
            if event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    # Get list of files in folder
                    file_list = os.listdir(folder)
                except: # pylint: disable=w0702
                    file_list = []
                fnames = [
                    f
                    for f in file_list
                    if os.path.isfile(os.path.join(folder, f))
                    and f.lower().endswith((".m"))
                ]
                self.__window["-FILE LIST-"].update(fnames)
            elif event == "-FILE LIST-":  # A file was chosen from the listbox
                try:
                    self.mapping_windows()
                    self.__coms.send_request('Matlab Disbatcher', ['add_mapping', values["-FILE LIST-"][0].replace(".m",''), "None", "Example"])
                except: # pylint: disable=w0702
                    pass
            elif event == "-MATCODE-":
                func = values["-MATCODE-"][0]
                self.__mat_lab_code_requst_num  = self.__coms.send_request('Matlab Disbatcher', ['dispatch_fucntion', func])


        super().set_status("Complete")
        self.__window.close()
    def mapping_windows(self):
        '''
            This function helps the user set up a mapping from data types.
        '''
        #build gui 
        database_display = [sg.Listbox(size=(80, 10), enable_events=True,  key="-DATABASE FEILDS-", values=[], no_scrollbar=True)],
        input_display = [
            [
                sg.Text('Input field', size= (10,5)), 
                sg.Input(key='-INPUT FIELD-')
            ],
            [
                sg.Text('Output field', size= (10,5)), 
                sg.Input(key='-OUTPUT FIELD-')
            ],
        ]
        button_dispaly = [
            [
                sg.Button('Submit'),
                sg.Button('Cancel'),
            ]
        ]

        layout = [
            [database_display, input_display],
            [button_dispaly] 
            ]

        window = sg.Window('Mapping Edditor: ', layout=layout, modal=True)

        request_num = -1
        db_list = None
        input_field = "None"
        output_field = "None"

        while (True):
            event, values = window.read(timeout=20)
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == sg.TIMEOUT_EVENT:
                #get db feilds list
                if request_num == -1:
                    request_num  = self.__coms.send_request('Data Base', ['get_tables_str_list'])
                else : #if we have check to see if there is a return value
                    db_list = self.__coms.get_return('Data Base', request_num)
                if db_list is not None: 
                    # if the return time is not none then we update the code
                    window['-DATABASE FEILDS-'].update(db_list)
                    #reset for next pass now
                    db_list = None
            if event == 'Submit':
                window.close()
                return input_field, output_field
            if event == '-INPUT FIELD-':
                input_field = values[0]
            if event == '-OUTPUT FIELD-':
                output_field = values[0]
            if event == 'Cancel':
                window['-INPUT FIELD-'].update("")
                window['-OUTPUT FIELD-'].update("")
        print(values)