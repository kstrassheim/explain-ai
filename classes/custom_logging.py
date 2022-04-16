from time import time, strftime, gmtime

class BackgroundColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Logger():
    def __init__(self, verbose:bool=True):
        self.verbose = verbose
    def get_timestamp(self)->float:
        return time()
    def log(self, msg:str):
        if (self.verbose): print(msg)
    def log_info(self, msg:str):
        if (self.verbose): print(f"{BackgroundColors.OKCYAN}{msg}{BackgroundColors.ENDC}")
    def log_warning(self, msg:str):
        if (self.verbose): print(f"{BackgroundColors.WARNING}{msg}{BackgroundColors.ENDC}")
    def log_error(self, msg:str):
        if (self.verbose): print(f"{BackgroundColors.FAIL}{msg}{BackgroundColors.ENDC}")
    def log_success(self, msg:str):
        if (self.verbose): print(f"{BackgroundColors.OKGREEN}{msg}{BackgroundColors.ENDC}")
    def get_duration(self, timestamp_begin:float):
        return time() - timestamp_begin
    def get_duration_str(self, timestamp_begin:float):
        return strftime('%H:%M:%S.{} %Z'.format(repr(time()).split('.')[1][:3]),gmtime(self.get_duration(timestamp_begin)))
    def log_duration(self, msg:str, timestamp_begin:float):
        if (self.verbose): print(f"{BackgroundColors.OKBLUE}{msg} {self.get_duration_str(timestamp_begin)}{BackgroundColors.ENDC}")