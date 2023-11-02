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
        self.__mat_lab_folder_requst_num = -1
        self.__fields_request_num = -1
        self.__avaible_matlab = None
        self.__avaible_matlab_folders = None
        self.__message_map = {
            '-PRELOGS-' : [],
            '-THREADS-' : [],
            '-LOGS-' : [],
        }
        self.__message_map_matlab_thread_report = {}
        self.__save_report = ['No save in progress', 0]
        self.__file_list_column = [
            [
            sg.Text("Find MatLab code:"),
            sg.In(size=(40, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
            sg.Button('Add folder to Matlab Path.', key='-ADD PATH-')
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

        self.__file_viewer =[
            [sg.Listbox(size=(160, 10), enable_events=True,  key="-FILE_PATHS-", values=[])],
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
                    sg.Frame("Matlab folder paths", self.__file_viewer, title_color='blue', key="-FILE_PATHS-"),                    
                ],
                [
                    sg.Frame("Processing Flow", self.__processing_flow_viewer, title_color='blue', key="-PROCESS-"),
                ],
                [
                    sg.Button("Get Data From Data Base", key='-GET DATA-'),
                ]
            ]

        ]
        self.__window = sg.Window("CSE Ground", self.__layout, scaling=True)
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

                #get the active matlab folders
                if self.__mat_lab_folder_requst_num == -1: 
                    self.__mat_lab_folder_requst_num  = self.__coms.send_request('Matlab Disbatcher', ['get_matlab_file_paths'])
                else : #if we have check to see if there is a return value
                    self.__avaible_matlab_folders = self.__coms.get_return('Matlab Disbatcher', self.__mat_lab_folder_requst_num)
                if self.__avaible_matlab_folders is not None: 
                    # if the return time is not none then we update the code
                    self.__window['-FILE_PATHS-'].update(self.__avaible_matlab_folders)
                    #reset for next pass now
                    self.__avaible_matlab_folders = None
                    self.__mat_lab_folder_requst_num = -1
                
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
                    input_table, out_put_dict = self.mapping_windows()
                    self.__coms.send_request('Matlab Disbatcher', ['add_mapping', values["-FILE LIST-"][0].replace(".m",''), input_table, out_put_dict]) #create the mapping in the dispacher, the last arg just checks to see if it is a list type
                    try:
                        self.__coms.send_request('Data Base', ['create_table_external', out_put_dict]) # create the need data base structure.
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
            elif event == '-ADD PATH-':
                # print(values["-FOLDER-"])
                self.__coms.send_request('Matlab Disbatcher', ['add_folder_path', values["-FOLDER-"]])


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
                sg.Text(f'Number of inputs: {0}', key='-TEXT NUM INPUTS-'),
                sg.Button('Add Input'),
            ],
            [
                sg.Text('Output table (New table)', size= (10,5)), 
                sg.Input(key='-OUTPUT TABLE-', enable_events=True),
            ],
            [
                sg.Text(f'Name of idex feild (Optional): '),
                sg.Input(key='-TEXT FEILD IDX-', enable_events=True),

            ],
            [
                sg.Text(f'Number of output tables: {0}', key='-TEXT NUM OUTPUTS TABLES-'),
                sg.Button('Add output table'),
            ],
            [
                sg.Text('Output field (New field)', size= (10,5)), 
                sg.Input(key='-OUTPUT FIELD-', enable_events=True),
            ],
            [
                sg.Text('Output field type (int(64), float(64), string, bool, bigint'),
                sg.Input(key='-OUTPUT FIELD TYPE-', enable_events=True),
            ],
            [
                sg.Text(f'Number of output feilds: {0}', key='-TEXT NUM OUTPUTS-'),
                sg.Button('Add output feild'),
            ],
        ]
        button_dispaly = [
            [
                sg.Button('Submit'),
                sg.Button('Cancel')
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
        output_dict = {} #dictinarl one key per table, then each key maps to a list of input vals.  
        input_count = 0
        output_feild_cout = 0
        output_table_cout = 0

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
                if input_count == 0:
                    sg.popup("No inputs added!!!")
                elif output_table_cout ==- 0:
                    sg.popup("No output tables added!!!")
                elif output_feild_cout == 0:
                    sg.popup("No output feilds added!!!")
                else :
                    window.close()
                    return input_lsit, output_dict
            if event == 'Cancel':
                window['-INPUT FIELD-'].update("")
                window['-OUTPUT FIELD-'].update("")
                window['-INPUT TABLE-'].update("")
            if event == 'Add Input':
                if(values['-INPUT TABLE-'] != '') and (values['-INPUT FIELD-'] != ''):
                    input_lsit.append((values['-INPUT TABLE-'], values['-INPUT FIELD-']))
                    input_count += 1
                    window['-INPUT FIELD-'].update("")
                    window['-INPUT TABLE-'].update("")
                    window['-TEXT NUM INPUTS-'].update(f'Number of inputs: {input_count}')
            if event == 'Add output feild':
                try: 
                    if (values['-OUTPUT FIELD-'] != '') and (values['-OUTPUT FIELD TYPE-'] != ''):
                        output_dict[values['-OUTPUT TABLE-']].append((values['-OUTPUT FIELD-'], values['-OUTPUT FIELD TYPE-']))
                        output_feild_cout += 1
                        window['-OUTPUT FIELD-'].update("")
                        window['-OUTPUT FIELD TYPE-'].update("")
                        window['-TEXT NUM OUTPUTS-'].update(f'Number of output feilds:  {output_feild_cout}')
                except :
                    sg.popup("Invaild table")
            if event == 'Add output table':
                if values['-OUTPUT TABLE-'] != '':
                    output_dict[values['-OUTPUT TABLE-']] = [('input_idx_db', values['-TEXT FEILD IDX-'])]
                    output_table_cout += 1
                    window['-TEXT NUM OUTPUTS TABLES-'].update(f'Number of output tables:  {output_table_cout}')
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

        window = sg.Window('Data base viewer: ', layout=layout)
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
    def make_matlab_thread_report(self, args):
        '''
            This funciton creats a report for the thread

            Input :
                args[0] : thread name
                args[1] : status
        '''
        self.__message_map_matlab_thread_report[args[0]] = args[1]
    def make_save_report(self, args):
        '''
            this function is how the db class reports on how much data it is saving.

            Inputs:
                args[0] : Data group being saved
                args[1] : (current row / total rows) * 100 (precent of data saved.)
        '''
        self.__save_report = [args[0], args[1]]
    def matlab_threading_report_disp(self):
        '''
            This function displays the matlab threading report disp
        '''
        #build gui 
        thread_disp = []

        for thread_name  in self.__message_map_matlab_thread_report:
            thread_disp.append([sg.Text(text = (thread_name + ":" + self.__message_map_matlab_thread_report[thread_name]), key=thread_name)])

        layout = [
            [threadWrapper],
            [
                sg.Text('Data base saving progress'),
                sg.ProgressBar(100, orientation='h', expand_x=True, size=(20, 20),  key='-PBAR-'),
                sg.Text('Data from thread: ', key='-THREAD SAVE-')
            ]
        ]

        window = sg.Window('Thread reporter: ', layout=layout, scaling=True)
        requests_ids = []
        while (True):
            event, values = window.read(timeout=20)
            if event == "Exit" or event == sg.WIN_CLOSED:
                self.__save_report = ['No save in progress', 0]
                return
            else :
                #update thread reports
                for thread_name in self.__message_map:
                    requests_ids.append(self.__coms.send_request([thread_name,'get_status']), thread_name, False)
                done = False
                while(not done):
                    done = True # set done to true everytime to make our check at the end work
                    idx = 0 #reset index to zero.
                    for request in requests_ids:
                        current_check = self.__coms.check_request('Data Base', request[0])
                        if(current_check):#remeber that we added the request in order, so we can index the input_table by keeping track of where we are in the request list
                            data = self.__coms.get_return('Data Base', request[0]) #collect data for completed request to data base.
                            window.update[request[1]] = data
                            requests_ids[idx][2] = True#after we have collected and added all the data mark the request as complete.
                        done = (done and requests_ids[idx][2]) # we AND all the request together so that why when they are all done we drop out of the loop.
                        idx += 1 #incrament the idx
                requests_ids.clear()
                #update progress bar
                window.update['-THREAD SAVE-'] = self.__save_report[0]
                window.update["-PBAR-"] = self.__save_report[1]
            

        
