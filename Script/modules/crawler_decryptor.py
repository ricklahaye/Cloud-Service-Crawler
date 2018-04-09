#!/usr/bin/python2.7
import logging, os, time, datetime, sqlite3, sys
from Registry import Registry
from modules.crawler_conf import crawler_Settings

class decryptor:
    def __init__(self, loggerName):
        # Initializes worker settings
        self.settings = crawler_Settings()
        self.logger = logging.getLogger(loggerName)
        self.logger.info("workers got access to settings and initalized the logger...")

    def google_read(self, user, mount_dir):
        print("==================== Google ====================")
        google_cfg = os.path.join(mount_dir, "Users/", user, "AppData/Local/Google/Drive/user_default/sync_config.db")   # db
        google_db = os.path.join(mount_dir, "Users/", user, "AppData/Local/Google/Drive/user_default/snapshot.db")      # db

        print(google_cfg)

        conn = sqlite3.connect(google_cfg)          # connect to db file under var google_cfg
        c = conn.cursor()                           # set var

        # Root folder
        # index 0: entry_key
        # index 2: value
        c.execute('SELECT * FROM data WHERE entry_key = "root_config__0"')
        output = list(c.fetchone())              # set result to var output
        output.pop(1)
        print(output)

        # User Account
        c.execute('SELECT * FROM data WHERE entry_key = "user_email"')
        output = list(c.fetchone())
        output.pop(1)
        print(output)


        print("\n" + google_db)
        conn = sqlite3.connect(google_db)
        c = conn.cursor()

        # Local Files on disk
        # index 2: file
        # index 3: modified epoch
        # index 6: doc type
        print("* Files on disk according to Google Drive: ")
        c.execute('SELECT * FROM local_entry')
        output = c.fetchall()
        for i in output:                    # for each hit
            i = list(i)                         # create list so we can change index
            output = []

            if isinstance(i[3], int):           # if record is int, thus a file, calculate time modified
                i[3] = "Modified: " + datetime.datetime.fromtimestamp(i[3]).strftime('%Y-%m-%d %H:%M:%S')
            else:
                i[3] = "Modified: unknown"

            if i[6] == 0:                       # if field 6 is 0 then file
                i[6] = "File"
            elif i[6] == 1:                     # if field 6 is 1 then directory
                i[6] = "Folder"

            output.extend([i[2], i[3], i[6]])
            print(output)
            # print(i[2], i[3], i[6])             # print output

        # Cloud files last seen on server
        # index 1: file
        # index 2: modified epoch
        # index 3: created epoch
        # index 5: doc type
        # index 6: removed epoch
        print("\n* Cloud files last seen on server according to Google Drive: ")
        c.execute('SELECT * FROM cloud_entry')
        output = c.fetchall()
        for i in output:                    # for each hit
            i = list(i)                         # create list so we can change index
            output = []

            if isinstance(i[2], int):           # if record is int, thus a file, calculate time modified
                i[2] = "Modified: " + datetime.datetime.fromtimestamp(i[2]).strftime('%Y-%m-%d %H:%M:%S')
            else:
                i[2] = "Modified: unknown"
            if i[5] == 1:                       # if field 5 is 0 then file
                i[5] = "File"
            elif i[5] == 0:                     # if field 5 is 1 then directory
                i[5] = "Folder"
            output.extend([i[1], i[2], i[5]])
            if isinstance(i[6], int):           # if record is int, calculate time removed
                if i[6] != 0:
                    i[6] = "Removed: " + datetime.datetime.fromtimestamp(i[6]).strftime('%Y-%m-%d %H:%M:%S')
                elif i[6] == 0:
                    i[6] = "Removed: no"
                output.append(i[6])
            print(output)
        print("==================== Google ====================")

    def onedrive_read(self, user, mount_dir):
        # Onedrive is an ini file, ini files can be read with configparse, but the file contains unicode characters which gives error with module
        # ini is binary format, not ascci
        # therefore OS binaries/tools like sed, nano, vim and grep do not work either
        # workaround: use windows.., or read file and do no filtering/data manipulation

        ntuser = os.path.join(mount_dir, "Users/", user, "NTUSER.DAT")


        # onedrive_dir=mount_dir + 'Users/' + user + '/AppData/Local/Microsoft/OneDrive/settings/Personal/'
        # for filename in os.listdir(onedrive_dir):      # for each file in dir
        #     filename_length = len(filename)                      # set length of name
        #     if filename_length > 16 and filename.endswith('.ini'):                            # then prob user ini
        #         with open(onedrive_dir + filename, 'r') as f:  # open file
        #         #     print(f.readlines().decode('ascii'))cd C
        #             os.system('head -1 ' + onedrive_dir + filename)
        print("\n==================== OneDrive ====================")
        reg = Registry.Registry(ntuser)
        key = reg.open("Software\\Microsoft\\OneDrive\\Accounts\\Personal")
        for v in key.values():
            # print v.name()
            if v.value_type() == Registry.RegSZ and v.name() == "UserEmail":
                print("OneDrive user email: " + v.value())
            if v.value_type() == Registry.RegSZ and v.name() == "UserFolder":
                print("OneDrive user folder: " + v.value())
        print("==================== OneDrive ====================")

    def dropbox_password(self, mount_dir, binaries_dir): # get local user account password
        print("\n==================== Dropbox ====================")

        dropbox_system_hive = os.path.join(mount_dir, "Windows/System32/config/SYSTEM") # hive location
        dropbox_security_hive = os.path.join(mount_dir, "Windows/System32/config/SECURITY")
        cmd = os.path.join(binaries_dir, 'working_binaries/Dropbox/lsasecrets') + ' --system=' + dropbox_system_hive +  ' --security=' + dropbox_security_hive + ' --secret=DefaultPassword'
        #print(repr(cmd))   # debug parameter to see what will get inserted into binary
        password = os.popen(cmd).read()
        password = password.strip('\n\n')                               # strip new line
        print("Dropbox Local User Account Password: " + password)     # password of user account
        return str(password.translate(None, '\x00'))

    def dropbox_keys(self, user, mount_dir, password, binaries_dir): # get dropbox decrypt key by filling in local user account password
        cmd = 'ls ' + os.path.join(mount_dir, 'Users/', user, 'AppData/Roaming/Microsoft/Protect/') + ' | grep \"^S-\"'
        sid = os.popen(cmd).read()
        sid = sid.strip("\n")
        print('Dropbox Local User Account SID: ' + sid)
        masterkey = os.path.join(mount_dir, "Users/", user, "AppData/Roaming/Microsoft/Protect/", sid)
        #password = raw_input("Enter above password: ")
        ntuser = os.path.join(mount_dir, "Users/", user, "NTUSER.DAT")
        cmd = os.path.join(binaries_dir, "working_binaries/Dropbox/dbx-key-win-dpapi.py") + " --masterkey=" + masterkey + " --sid=" + sid + " --password=" + password + " --ntuser=" + ntuser
        # print(repr(cmd))   # debug parameter to see what will get inserted into binary
        dbx_key = os.popen("{}".format(cmd)).read()
        print(dbx_key)
        for line in dbx_key.split("\n"):
            if "DBX key" in line:
                return line.split("\t")[1]
            else:
                pass

    def dropbox_decode(self, user, mount_dir, dropbox_key, binaries_dir):   # decode dbx and save to /tmp
        dropbox_dbx = os.path.join(mount_dir, "Users/", user, "AppData/Local/Dropbox/instance1/config.dbx") # dbx
        dropbox_dbx_file = os.path.join(mount_dir, "Users/", user, "AppData/Local/Dropbox/instance1/filecache.dbx") # dbx
        #password = raw_input("Enter above DBX Key: ")
        cmd = os.path.join(binaries_dir, "working_binaries/Dropbox/sqlite-dbx-tux64") + " -key " + dropbox_key + " " + dropbox_dbx + " \".backup /tmp/config.db\""
        #print(repr(cmd))   # debug parameter to see what will get inserted into binary
        os.system(cmd)
        cmd = os.path.join(binaries_dir, "working_binaries/Dropbox/sqlite-dbx-tux64") + " -key " + dropbox_key + " " + dropbox_dbx_file + " \".backup /tmp/filecache.db\""
        os.system(cmd)

    def dropbox_read(self):
        conn = sqlite3.connect("/tmp/config.db")        # connect to db file under var google_cfg
        c = conn.cursor()

        c.execute('SELECT * FROM config WHERE key = "email"')   # email
        output = list(c.fetchone())
        print(output)

        c.execute('SELECT * FROM config WHERE key = "userdisplayname"') # user
        output = list(c.fetchone())
        print(output)

        c.execute('SELECT * FROM config WHERE key = "dropbox_path"') # rootfolder
        output = list(c.fetchone())
        print(output)

        conn = sqlite3.connect("/tmp/filecache.db")        # connect to db file under var
        c = conn.cursor()

        #CREATE TABLE file_journal (id INTEGER PRIMARY KEY NOT NULL,server_path TEXT NOT NULL UNIQUE,parent_path TEXT NOT NULL,extra_pending_details PENDINGDETAILS2,force_reconstruct INTEGER CHECK (force_reconstruct=1),local_sjid INTEGER,local_host_id INTEGER,local_filename TEXT,local_blocklist BYTETEXT CHECK(local_blocklist IS NULL OR TYPEOF(local_blocklist) == 'text'),local_infinite_details INFINITEDETAILS,local_size INTEGER,local_mtime INTEGER,local_ctime INTEGER,local_dir INTEGER,local_attrs ATTRIBUTETEXT,local_timestamp INTEGER,local_user_id INTEGER,local_sync_type INTEGER,updated_sjid INTEGER,updated_host_id INTEGER,updated_filename TEXT,updated_blocklist BYTETEXT CHECK(updated_blocklist IS NULL OR TYPEOF(updated_blocklist) == 'text'),updated_size INTEGER,updated_mtime INTEGER,updated_dir INTEGER,updated_timestamp INTEGER,updated_user_id INTEGER,updated_attrs ATTRIBUTETEXT,updated_sync_type INTEGER);

        # 1|2604326896:/getting started with dropbox paper.url|2604326896:/|||4|1|Getting Started with Dropbox Paper.url|kPIn4Te4OtTntzDqxmIUxueJOLhkWYXZu2dHeK50XJc||240|1520512908|1520512908|0|{"dropbox_mute": {"mute_key": {"data": "AQAAAAAAAAAA"}, "mute": {"data": "MQ=="}}}|1520512908|81554767|1|||||||||||
        # 2|2604326896:/getting started with dropbox.pdf|2604326896:/|||2|1|Getting Started with Dropbox.pdf|LiKDtWYdKc4fsgRAZdok9KHJRrzfjj8Dkx4Kh2Q0Ooo||1467194|1520512907|1520512907|0|{"dropbox_mute": {"mute_key": {"data": "AQAAAAAAAAAA"}, "mute": {"data": "MQ=="}}}|1520512908|81554767|1|||||||||||

        print("\n* Files according to Dropbox file cache: ")
        c.execute('SELECT * FROM file_journal')
        output = c.fetchall()
        for i in output:                    # for each hit
            i = list(i)                         # create list so we can change index
            output = []

            output.extend([i[1], i[7]])
            print(output)
        print("==================== Dropbox ====================")

    def icloud_read(self, user, mount_dir):
        print("==================== iCloud ====================")
        icloud_client_cfg = os.path.join(mount_dir, "Users/", user, "AppData/Local/Apple Inc/CloudKit/iCloudDrive/ckcachedatabase.db")
        icloud_client_db = os.path.join(mount_dir, "Users/", user, "AppData/Local/Apple Inc/iCloudDrive/client.db")
        icloud_server_db = os.path.join(mount_dir, "Users/", user, "AppData/Local/Apple Inc/iCloudDrive/server.db")   # db
        # print(icloud_client_cfg)
        conn = sqlite3.connect(icloud_client_cfg)        # connect to db file under var google_cfg
        c = conn.cursor()

        c.execute('SELECT * FROM PCSData')
        output = list(c.fetchone())
        print("User: " + output[0])

        conn = sqlite3.connect(icloud_client_db)        # connect to db file under var google_cfg
        c = conn.cursor()

        print("\n* Files according to Local file cache: ")
        c.execute('SELECT * FROM items')
        output = c.fetchall()
        for i in output:                    # for each hit
            i = list(i)                         # create list so we can change index
            output = []

            output.extend([i[18], i[20]])
            print(output)

        conn = sqlite3.connect(icloud_server_db)        # connect to db file under var google_cfg
        c = conn.cursor()

        print("\n* Files according to Server file cache: ")
        c.execute('SELECT * FROM server_items')
        output = c.fetchall()
        for i in output:                    # for each hit
            i = list(i)                         # create list so we can change index
            output = []

            output.append(i[14])
            print(output)

        print("==================== iCloud ====================")

# snapshot.db only contains files if client has been restarted, otherwise they will be present in temp files that will get loaded on next start
