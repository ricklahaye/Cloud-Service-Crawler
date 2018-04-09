import threading, logging, ssdeep
from modules.crawler_conf import crawler_Settings

class workers:
    def __init__(self, loggerName):
        # Initializes worker settings
        self.settings = crawler_Settings()
        self.logger = logging.getLogger(loggerName)
        self.logger.info("workers got access to settings and initalized the logger...")

    # Worker to read files passed to the crawler
    def fileReader(self, filePath, fileName):
        if (filePath != ""):
            try:
                # Opens the file for reading
                self.logger.info("Opening file {} for reading...".format(filePath))
                self.hashFile = open(filePath, mode="r")
                for self.line in self.hashFile:
                    # for each line it sends to the settings class to be appended to the hashList
                    if (self.line != "\n"):
                        if("ssdeep" in self.line):
                            self.settings.setHashList("{}".format(self.line))
                        else:
                            self.settings.setHashList("{},{}".format(fileName.split("-")[0], self.line.split(",")[0]))
                            self.logger.debug("Adding to hashlist the following line: {}".format(self.line))
                    else:
                        pass
                self.hashFile.close()
            except Exception as err:
                # Loggs if any error happened during file operations
                self.logger.error("Reading the file failed with error: {}".format(err))
                pass
        else:
            self.logger.error("Reading Worker received an empty filename")
            return

    def mountCrawler(self, fileName):
        if (fileName != ""):
            try:
                # Opens the file for reading
                self.logger.info("Hashing {}...".format(fileName))
                self.settings.setHashListComp("{},{}".format(ssdeep.hash_from_file(fileName), fileName))
            except Exception as err:
                # Loggs if any error happened during file operations
                self.logger.error("Reading the file failed with error: {}".format(err))
                pass
        else:
            self.logger.error("Reading Worker received an empty filename")
            return