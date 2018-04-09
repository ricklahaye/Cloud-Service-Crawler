###################################################
# Program created by Joao Marques and Rick Lahaye #
# for the Cyber Crime and Forensics course of OS3 #
###################################################
import sys, logging, ntpath, ssdeep, threading
from os import walk, path
from time import sleep
from modules.crawler_conf import crawler_Settings
from modules.crawler_workers import workers
from modules.crawler_decryptor import decryptor
from modules.crawler_recursor import recursor

def main(argv):
### Gathering of the hashes ###############################################################
  threadCounter = 0
  threadHolder = []
  workers_file_dispatcher = workers("root.workers")
  workers_dir_dispatcher = []

  # Parses the arguments, if its a file it calls the function
  if (parserArgs.file != None):
    logger.info("Reading file: {}".format(parserArgs.file))
    workers_file_dispatcher.fileReader(parserArgs.file, ntpath.basename(parserArgs.file))
  # Else it will create threads to read the hashes into a list
  else:
    recurse = recursor("root.Recursor")
    logger.info("Walking directory: {}".format(parserArgs.dir))
    for filePath in recurse.find_files(parserArgs.dir.split("\n")):
      logger.debug("  File found: {}".format(filePath))
      workers_dir_dispatcher.append(workers("root.Thread-{}".format(threadCounter + 1)))
      threadHolder.append(threading.Thread(target=workers_dir_dispatcher[threadCounter].fileReader, args=(filePath, ntpath.basename(filePath) ,)))
      threadCounter += 1
      logger.debug("Thread Counter increased")
    
    # Starts the threads
    threadCounter = 0
    for thread in threadHolder:
      while threading.activeCount() >= 1000:
        sleep(1)
        logger.warning("Thread queue is full!")
      thread.start()
      logger.debug("Thread {} started...".format(threadCounter + 1))
      threadCounter += 1

    # Waits for the threads to finish executing
    for thread in threadHolder:
      thread.join()

    # Merges the threads into a single database file
    database_merger()
###########################################################################################
  
### Recursion and gathering of file locations #############################################
  threadCounter = 0
  threadHolder = []
  workers_file_dispatcher = workers("root.Workers")
  workers_dir_dispatcher = []
  file_list = []

  recurse = recursor("root.Recursor")
  if (parserArgs.scan_directory is None):
    logger.info("Walking directory: {}".format(parserArgs.mount_point))    
    file_list = recurse.find_files(parserArgs.mount_point.split("\n"))
  else:
    logger.info("Walking directory: {}".format(parserArgs.scan_directory))        
    file_list = recurse.find_files(parserArgs.scan_directory)
  
  for filepath in file_list:
    logger.debug("creating thread")
    workers_dir_dispatcher.append(workers("root.Thread-{}".format(threadCounter + 1)))
    threadHolder.append(threading.Thread(target=workers_dir_dispatcher[threadCounter].mountCrawler, args=(filepath,)))
    threadCounter += 1
    logger.debug("Thread Counter increased")
  
  # Starts the threads
  threadCounter = 0
  for thread in threadHolder:
    while threading.activeCount() >= 1000:
      sleep(1)
      logger.warning("Thread queue is full!")
    thread.start()
    logger.debug("Thread {} started...".format(threadCounter + 1))
    threadCounter += 1

  # Waits for the threads to finish executing
  for thread in threadHolder:
    thread.join()

  for fuzzyHash in settings.getHashList():
    for filesystemHash in settings.getHashListComp():
      if ("-blocksize" not in fuzzyHash and "-blocksize" not in filesystemHash):
        if (int(fuzzyHash.split(",")[1].split(":")[0]) == int(filesystemHash.split(":")[0])):
          if (ssdeep.compare(fuzzyHash.split(",")[1], filesystemHash.split(",")[0]) >= 90):
            logger.debug("[+]A {} file was found in: {}".format(fuzzyHash.split(",")[0], filesystemHash.split(",")[1]))
            settings.setServicesFound("{},{}".format(fuzzyHash.split(",")[0], filesystemHash))
          else:
            pass
        else:
          pass
      else:
        pass
  logger.debug(list(set(settings.getServicesFound())))

  fuzzyHashes = {"dropbox":0, "onedrive":0, "google":0, "megasync":0, "icloud":0}
  for fuzzyHash in list(set(settings.getHashList())):
    logger.debug(fuzzyHash)
    if("dropbox" in fuzzyHash.split(",")[0]):
      fuzzyHashes["dropbox"] += 1
    elif("onedrive" in fuzzyHash.split(",")[0]):
      fuzzyHashes["onedrive"] += 1
    elif("google" in fuzzyHash.split(",")[0]):
      fuzzyHashes["google"] += 1
    elif("megasync" in fuzzyHash.split(",")[0]):
      fuzzyHashes["megasync"] += 1
    elif("icloud" in fuzzyHash.split(",")[0]):
      fuzzyHashes["icloud"] += 1
    else:
      pass

  filesystemHashes = {"dropbox":0, "onedrive":0, "google":0, "megasync":0, "icloud":0}
  for filesystemHash in list(set(["{0[0]},{0[1]}".format(item.split(",")) for item in settings.getServicesFound()])):
    if("dropbox" in filesystemHash.split(",")[0]):
      filesystemHashes["dropbox"] += 1
    if("onedrive" in filesystemHash.split(",")[0]):
      filesystemHashes["onedrive"] += 1
    if("google" in filesystemHash.split(",")[0]):
      filesystemHashes["google"] += 1
    if("megasync" in filesystemHash.split(",")[0]):
      filesystemHashes["megasync"] += 1
    if("icloud" in filesystemHash.split(",")[0]):
      filesystemHashes["icloud"] += 1
    else:
      pass

  print("FuzzyHashes in database:\n  Dropbox:{}\n  Onedrive:{}\n  Google:{}\n  Megasync:{}\n  Icloud:{}\n  ".format(fuzzyHashes["dropbox"], fuzzyHashes["onedrive"], fuzzyHashes["google"], fuzzyHashes["megasync"], fuzzyHashes["icloud"]))
  print("FuzzyHashes matches:\n  Dropbox:{}\n  Onedrive:{}\n  Google:{}\n  Megasync:{}\n  Icloud:{}\n  ".format(filesystemHashes["dropbox"], filesystemHashes["onedrive"], filesystemHashes["google"], filesystemHashes["megasync"], filesystemHashes["icloud"]))

############################################################################################

### Choice of operation ####################################################################
  decrypt = decryptor("root.decryptor")
  services_available = "Options Available:"
  service_num = {"dropbox":0, "onedrive":0, "google":0, "megasync":0, "icloud":0}
  service_counter = 0
  for service in list(set([item.split(",")[0] for item in settings.getServicesFound()])):
    service_counter += 1
    service_num[service] = service_counter
    services_available += "\n\t{}. {}".format(service_counter, service)

  service_counter += 1
  service_num["quit"] = service_counter
  services_available += "\n\t{}. Quit".format(service_counter)

  while True:
    print(services_available)
    option = raw_input("Choose one of the options (by number):")
    try:
      if (int(option) == service_num["dropbox"] and int(option) != 0):
        try:
          dropbox_password = decrypt.dropbox_password(parserArgs.mount_point, path.dirname(path.realpath(sys.argv[0])))   
          dropbox_key = decrypt.dropbox_keys(parserArgs.user, parserArgs.mount_point, dropbox_password, path.dirname(path.realpath(sys.argv[0])))
          decrypt.dropbox_decode(parserArgs.user, parserArgs.mount_point, dropbox_key, path.dirname(path.realpath(sys.argv[0])))
          decrypt.dropbox_read()
        except Exception as err:
          print("Could not decode dropbox, the following error was thrown: {}".format(err))
      elif (int(option) == service_num["google"] and int(option) != 0):
        try:
          decrypt.google_read(parserArgs.user, parserArgs.mount_point)
        except Exception as err:
          print("Could not decode google, the following error was thrown: {}".format(err))
      elif (int(option) == service_num["onedrive"] and int(option) != 0):
        try:
          decrypt.onedrive_read(parserArgs.user, parserArgs.mount_point)
        except Exception as err:
          print("Could not decode onedrive, the following error was thrown: {}".format(err))      
      # elif (int(option) == service_num["megasync"] and int(option) != 0):
      #   try:
      #     print("Decoder in construction!")
      #   except Exception as err:
      #     print("Could not decode megasync, the following error was thrown: {}".format(err))
      elif (int(option) == service_num["icloud"] and int(option) != 0):
        try:
          decrypt.icloud_read(parserArgs.user, parserArgs.mount_point)
        except Exception as err:
          print("Could not decode icloud, the following error was thrown: {}".format(err))
      elif (int(option) == service_num["quit"] and int(option) != 0):
        break
      else:
        print("Choosen option not available! Choose another one!")
    except ValueError:
      print("Option is not an integer!")

# This function creates a database file and writes to it the list of hashes, sorted and with duplicates and empty lines removed
def database_merger():
  try:
    database = open(path.join(path.dirname(path.realpath(sys.argv[0])),'hashes.db'), mode="w")
    logger.debug("Database file created")
    list_placeholder = sorted(set([item for item in settings.getHashList() if item.split('\n')[0] != '']), key=sortingKey)
    for item in list_placeholder:
      database.write("{}\n".format(item))
    #logger.debug("Database file writen to with the following content: \n\t{}".format(list_placeholder))
    database.close()
    logger.debug("Database file closed...")
  except Exception as error:
    logger.error("Failed to open database file with error: {}".format(error))

# This function is used to properly sort the lines of the database but keeping the fileds description in first place
def sortingKey(value):
  if("ssdeep" in value):
    return int("0")
  else:
    return int((value.split(":")[0]).split(",")[1])

if __name__ == "__main__":
   # Initializes crawler settings
  settings = crawler_Settings()
  logger = settings.getLogger()
  logger.info("Crawler settings finished initializing")
  parserArgs = settings.getArgsParser()
  main(sys.argv)
