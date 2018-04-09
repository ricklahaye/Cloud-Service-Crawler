import os, scandir, sys, logging
from timeit import default_timer as timer
from modules.crawler_conf import crawler_Settings

def func_timer(func_name):
    def real_decorator(func_run):
        def wrapper(*args, **kwargs):
            t1 = timer()
            value = func_run(*args, **kwargs)
            print("\nTime it took to run {}: {:.2f} seconds".format(func_name, float(timer() - t1)))
            return value
        return wrapper
    return real_decorator

class recursor(object):
    def __init__(self, loggerName):
        self.settings = crawler_Settings()
        self.logger = logging.getLogger(loggerName)
        self.logger.info("Recursor got access to settings and initalized the logger...")
        self.dir_list = []
        self.file_list = []

    ###### Not used for now...########################################################
    # @func_timer("find_directory")
    # def find_directory(self, search_path, search_dir):
    #     for self.path, self.dirnames, self.filenames in scandir.walk(search_path):
    #         # print path to all subdirectories first.
    #         for self.subdirname in self.dirnames:
    #             self.logger.debug("Looking at dir {}".format(os.path.join(self.path, self.subdirname)))
    #             if (self.subdirname in search_dir):
    #                 self.dir_list.append(os.path.join(self.path, self.subdirname))
    #     return self.dir_list
    ###################################################################################

    #@func_timer("find_files")
    def find_files(self, search_path):
        self.logger.debug("Entered find_files() with the following argument: {}".format(search_path))
        for self.dir in search_path:
            self.logger.info("Starting os.walk() on: {}".format(self.dir))
            for self.path, self._dirnames, self.filenames in scandir.walk(self.dir):
                self.logger.debug("Found:\n\t{}\n\t{}\n\t{}".format(self.path, self._dirnames, self.filenames))
                for self.filename in self.filenames:
                    self.file_list.append(os.path.join(self.path, self.filename))
        if(len(self.file_list) > 0):
            return self.file_list
        else:
            exit("Directory provided does not exist or it has no files!")