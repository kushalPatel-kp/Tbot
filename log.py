import os
import coloredlogs
import logging
import datetime
from Directory import Directory
from logging.handlers import TimedRotatingFileHandler

# Create a logger object.
# logger = logging.getLogger(__name__)
logger = logging.getLogger('TBOT_KAUS29')

# By default the install() function installs a handler on the root logger,
# this means that log messages from your code and log messages from the
# libraries that you use will all show up on the terminal.
coloredlogs.install(level='DEBUG')

# If you don't want to see log messages from libraries, you can pass a
# specific logger object to the install() function. In this case only log
# messages originating from that logger will show up on the terminal.
coloredlogs.install(level='DEBUG', logger=logger,
                    fmt='%(asctime)s :[%(levelname)s]:Line No. : %(lineno)d - %(message)s')

Directory().CreateDirectory("TradeLogs")
path = Directory().GetCurrentDirectory()+"\\TradeLogs\\"
time = datetime.datetime.now().strftime('%Y_%m_%d')

formatter = logging.Formatter(
    "%(asctime)s :[%(levelname)s]:Line No. : %(lineno)d - %(message)s")

handler = TimedRotatingFileHandler(
    path+time+'.log', when="midnight", interval=1)

handler.setFormatter(formatter)

logger.addHandler(handler)

def CleanLogFiles():

    path = os.getcwd() + "\\TradeLogs\\"

    log_file_list = os.listdir(path)
    log_file_list.sort(reverse=True)
    log_file_list = log_file_list[7:]

    for logFile in log_file_list:
        os.unlink(path + logFile)