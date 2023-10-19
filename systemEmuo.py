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
from logging_system_display_python_api.htmlParser import CSEHTMLParser


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
        self.__fields_request_num = -1
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
            [sg.Text('Data Base feilds: ')],
            [sg.Listbox(size=(80, 10), enable_events=True,  key="-DATABASE FEILDS-", values=[])],
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
                [
                    sg.Column(self.__file_list_column, element_justification='t'),
                    sg.VSeperator(),
                    sg.Column(self.__logs_viewer_column),
                ],
                [
                    sg.Frame("Processing Flow", self.__processing_flow_viewer, title_color='blue', key="-PROCESS-"),
                ],
                [
                    sg.Button("Get Data From Data Base", key='-GET DATA-'),
                ]
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
                
                #get db feilds list
                db_list = None
                if self.__fields_request_num == -1:
                    self.__fields_request_num  = self.__coms.send_request('Data Base', ['get_tables_str_list'])
                else : #if we have check to see if there is a return value
                    db_list = self.__coms.get_return('Data Base', self.__fields_request_num)
                if db_list is not None: 
                    # if the return time is not none then we update the code
                    self.__window['-DATABASE FEILDS-'].update(db_list)
                    #reset for next pass now
                    db_list = None
                    self.__fields_request_num = -1

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
                    input_table, output_field, out_field_type, input_field = self.mapping_windows()
                    self.__coms.send_request('Matlab Disbatcher', ['add_mapping', values["-FILE LIST-"][0].replace(".m",''), input_table, output_field, input_field, ('list' in out_field_type)]) #create the mapping in the dispacher, the last arg just checks to see if it is a list type
                    try:
                        self.__coms.send_request('Matlab Disbatcher', ['add_field_mapping', values["-FILE LIST-"][0].replace(".m",''), output_field, out_field_type]) # create the need data base structure.
                    except Exception as error :
                        self.__coms.print_message(f"Failed to create matlab mapping: {error}")
                    self.__mat_lab_code_requst_num = -1 #if everything goes right, we need to signal to the db display to update.
                except Exception as error : # pylint: disable=w0702
                    self.__coms.print_message(f"Failed to create matlab mapping: {error}")
            elif event == "-MATCODE-":
                func = values["-MATCODE-"][0]
                self.__mat_lab_code_requst_num  = self.__coms.send_request('Matlab Disbatcher', ['dispatch_fucntion', func])
            elif event == '-DATABASE FEILDS-':
                self.get_table_info(values['-DATABASE FEILDS-'][0])
            elif event == '-GET DATA-':
                self.get_data()

        super().set_status("Complete")
        self.__window.close()
    def mapping_windows(self):
        '''
            This function helps the user set up a mapping from data types.
            ARGS:
                None
            Returns:
                input_field, output_field, output type
        '''
        #build gui 
        database_display = [
            [sg.Text('Data Base feilds: ')],
            [sg.Listbox(size=(80, 10), enable_events=True,  key="-DATABASE FEILDS-", values=[])]
        ],
        input_display = [
            [
                sg.Text('Input Table  (Data  Base table name: None or active table)', size= (10,5)), 
                sg.Input(key='-INPUT TABLE-', enable_events=True)
            ],
            [
                sg.Text('Input field  (Feild Name: None or field in table)', size= (10,5)), 
                sg.Input(key='-INPUT FIELD-', enable_events=True)
            ],
            [
                sg.Text('Output field (Exsisting, or New field)', size= (10,5)), 
                sg.Input(key='-OUTPUT FIELD-', enable_events=True),
            ],
            [
                sg.Text('Output field type (int(64), float(64), string, bool, bigint, or list <type>'),
                sg.Input(key='-OUTPUT FIELD TYPE-', enable_events=True),
            ],
            [
                sg.Text('If you use list type, it will create a table that has two columns, one for the index, one for the return value of the defined type.')
            ],
        ]
        button_dispaly = [
            [
                sg.Button('Submit'),
                sg.Button('Cancel'),
                [
                    sg.Text(f'Number of inputs: {0}', key='-TEXT NUM INPUTS-'),
                    sg.Button('Add Input'),
                ]
            ]
        ]

        layout = [
            [database_display, input_display],
            [button_dispaly] 
        ]

        window = sg.Window('Mapping Edditor: ', layout=layout, modal=True)

        request_num = -1
        db_list = None
        input_lsit = []
        input_count = 0

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
                return values['-INPUT TABLE-'], values['-OUTPUT FIELD-'], values['-OUTPUT FIELD TYPE-'], values['-INPUT FIELD-']
            if event == 'Cancel':
                window['-INPUT FIELD-'].update("")
                window['-OUTPUT FIELD-'].update("")
                window['-INPUT TABLE-'].update("")
            if event == 'Add Input':
                input_lsit.append((values['-INPUT TABLE-'], values['-INPUT FIELD-']))
                input_count += 1
                window['-INPUT FIELD-'].update("")
                window['-INPUT TABLE-'].update("")
                window['-TEXT NUM INPUTS-'].update(f'Number of inputs: {input_count}')
                


    def get_table_info(self, table_name):
        '''
            This function helps the user see the data base table info
            ARGS:
                Table Name
            Returns:
                None
        '''
        #build gui 
        database_display = [
            [sg.Text('Data Base Feild: ')]
        ]

        layout = [
            [database_display]
        ]

        request_num = -1
        db_list = None

        while (True):
            #get db feilds list
            if request_num == -1:
                request_num  = self.__coms.send_request('Data Base', ['get_data_type', table_name])
            else : #if we have check to see if there is a return value
                db_list = self.__coms.get_return('Data Base', request_num)
            if db_list is not None: 
                # if the return time is not none then we update the code
                parser = CSEHTMLParser()
                parser.feed(str(db_list))
                data_obj = parser.get_data()
                
                layout.append([  
                    sg.Multiline(size=(80,10), key='-DATA OBJECT-', auto_size_text=True, default_text=data_obj)
                ])
                break 
        window = sg.Window('Mapping Edditor: ', layout=layout, modal=True)
        while True:
            event, values = window.read(timeout=20)
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
    def get_data(self):
        '''
            This function helps the user see the data base saved values
            ARGS:
                None
            Returns:
                None
        '''
        #build gui 
        database_display = [
            [sg.Text('Data Base stored info: ')],
            
        ]

        layout = [
            [database_display],
            [
                sg.Text("Table name:\t"),
                sg.Input(key='-INPUT TRABLE NAME-', enable_events=True)
            ],
            [
                sg.Text("Starting table idex: "),
                sg.Input(key='-INPUT START-', default_text=0, enable_events=True)
            ],
            [
                sg.Multiline(key='-INFO DISPALY-', size=(80,10))
            ],
            [
                sg.Button('Fetch data', key = '-FETCH-')
            ]

        ]

        request_num = -1
        db_list = None
        table_name = ''
        start = -1

        window = sg.Window('Mapping Edditor: ', layout=layout)
        while True:
            event, values = window.read(timeout=20)
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == '-INPUT TRABLE NAME-':
                table_name = values['-INPUT TRABLE NAME-']
            elif event == '-INPUT START-':
                start =  values['-INPUT START-']
            elif event == '-FETCH-':
                if(request_num != -1):
                    sg.popup("Please wait  already processing request.")
                elif(table_name == ''):
                    sg.popup("Please input table name.")
                else: # all things ready lest make the request
                    request_num  = self.__coms.send_request('Data Base', ['get_data_large', table_name, start])
            elif (request_num != -1):# Check to see if there is a return value for the request
                db_list = self.__coms.get_return('Data Base', request_num)
            if db_list is not None: 
                # if the return time is not none then we update the code
                window['-INFO DISPALY-'].update(db_list)
                request_num = -1
                db_list = None
