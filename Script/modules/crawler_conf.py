# This module initializes global variables to be used by the main script and all other imported modules
import argparse, logging, os, sys
from logging.handlers import RotatingFileHandler

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
       if cls not in instances:
            instances[cls] = cls(*args, **kw)
       return instances[cls]
    return _singleton

@singleton
class crawler_Settings:
  def __init__(self):
    # Setting up argument parser
    self.parser = argparse.ArgumentParser(prog='crawler.py', description='This script is a cloud service crawler that finds commonly used cloud services in a path.', usage='python %(prog)s (-f FILE | -d DIR) -t TARGET')
    self.reqGroup = self.parser.add_argument_group('Required')
    self.exclGroup = self.reqGroup.add_mutually_exclusive_group(required=True)
    self.exclGroup.add_argument("-f", "--file", help="Path to hashes file", action="store")
    self.exclGroup.add_argument("-d", "--dir", help="Path to directory containing hashes files", action="store")
    self.parser.add_argument("-u", "--user", help="Specify user", action="store", default="admin")
    self.parser.add_argument("-m", "--mount-point", help="Specify Mountpoint of the filesystem", action="store", required=True)
    self.parser.add_argument("-s", "--scan-directory", help="Specify directories to scan", action="append")
    self.parser.add_argument("-v", "--verbose", help="Show debugging information", action="store_true")
    self.parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    self.parserArgs = self.parser.parse_args()

    # Setting up logging
    self.logger = logging.getLogger("root")
    
    if (self.parserArgs.verbose):
      self.logger.setLevel(logging.DEBUG)
    else:
      self.logger.setLevel(logging.INFO)
   
    self.fileHandler = RotatingFileHandler(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),'crawler.log'), maxBytes=1000000, backupCount=5)
    self.fileHandler.setLevel(logging.INFO)
    self.consoleHandler = logging.StreamHandler()
    self.consoleHandler.setLevel(logging.DEBUG)
    self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    self.fileHandler.setFormatter(self.formatter)
    self.consoleHandler.setFormatter(self.formatter)
    self.logger.addHandler(self.fileHandler)
    self.logger.addHandler(self.consoleHandler)

    # Initialize global variables
    self.HashList = []
    self.HashListComp = []
    self.ServicesFound = []
  
  def getArgsParser(self):
    return self.parserArgs

  # Function to get the initialized central logger
  def getLogger(self):
    return self.logger

  # Function to read the HasList variable
  def getHashList(self):
    self.logger.debug("HashList being read...")
    return self.HashList

  # Function to write to list
  def setHashList(self, value):
    self.HashList.append(value)
    self.logger.debug("HashList being writen to...")

  # Function to read the HasList variable
  def getHashListComp(self):
    self.logger.debug("Filesystem HashList being read...")
    return self.HashListComp

  # Function to write to list
  def setHashListComp(self, value):
    self.logger.debug("Filesystem HashList writen to...")
    self.HashListComp.append(value)
  
  # Function to read the HasList variable
  def getServicesFound(self):
    self.logger.debug("Services found list being read...")
    return self.ServicesFound

  # Function to write to list
  def setServicesFound(self, value):
    self.logger.debug("Services found list being writen to...")
    self.ServicesFound.append(value)