# Logging Systems and Display Python API
This api written so that the user can send messages to the `message handler` class and then the system will display it to the user. \
NOTE: Different display interfaces are contatined on differnet branches. \
In addition this class can be used to send messages to threads. In the system.

![class structure](logging.png)

## Message Handler class
This class is the mail man of the systems. 
### Functions:
1. `__init__`: Constructor, this sets up the class. NOTE: That mutex locking is set up here as well.
2. `set_thread_handler`: This fuction is used so that the `message handler` can get access to the `thread  handler`.
3. `send_message_prement`: Send message that will not be erased after some time.
4. `print_message`: Send message that will be erased after some time.
5. `report_thread`: Send message that will appear under the threading report.
6. `report_bytes`: Send messges that will report the byte count.
7. `flush`: write message log to the screen.
8. `flush_prem`: write prement message log to screen.
9. `flusflush_thread_reporth`: write thread report to the screen. 
10. `flush_bytes`: write bytes to the screen.
11. `clear_disp` : clear the display. 
12. `run` : start the class, and refresh display at the refresh rate. 
11. `get_system_emuo` : returns the `system_emuo` class. (The class that is being used to actually display the info.)
12. `send_request` : This function mapps threading requests into the thread handler. 
13. `get_return` : This function mapps the return value of a thread to the caller. 

### HOW TO:
The main function that will be used is the `send_request` and `get_return` functions. When a request is sent, it will return an id. That id should be passed into get_return. `Get_return` will then go and check if that id has a return value. If if doesn't have a return value yet then it returns `None`. This is to avoid gride lock, and having to wait for the thread to finish. Thus the users should call  `get_return` periodically and check to see if the return value is `None`.

## Graphics Handler
This class is the formatter of the system.
### Function:
1. `__init__`: Sets up class, not that it class the `super()._init__(self.__coms)` this is the `systemEmuo` class. 
2. `write_message_log`: Passes the logs to the display class.
3. `send_message`: Adds a messages to the back log of messages that needs to be printed. 
4. `send_message_prement` : Adds a messages to the back log of prement messages that needs to be printed. 
5. `write_message_prement_log`: Passes the logs to the display class.
6. `report_thread`: addes the new report to the local varible to be displayed. 
7. `write_thread_report`: Formatts and sends the thread report to the display.
8. `write_byte_report`: Passes the byte report to the display. 
9. `report_byte`: Adds a byte report to the log.

### HOW TO:
This class is largely ment to be replace for new applications. In other words it should be application specific. When writing a new class, jsut make sure to match the structure of this class, and match the function names and it should work well with the system. 

## `systemEmuo`
This class handles the display. In this case is uses `pysimpleguis` to dispaly the information to the user. It has the format defined in the `__init__` function, and then the `run` function is to update the gui and get user input.

## `logging`
This class is a simple logger. Give it a file name and tell it to log messages when you want to. 