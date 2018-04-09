# Run

## Get User Password password
```
./lsasecrets --system=/mnt/Windows/System32/config/SYSTEM
--security=/mnt/Windows/System32/config/SECURITY
--secret=DefaultPassword

./lsasecrets --system=/mnt/Windows/System32/config/SYSTEM
--security=/mnt/Windows/System32/config/SECURITY --hex
```

## Get Dropbox decode keys
```
python2.7 dbx-key-win-dpapi.py
--masterkey=/mnt/Users/os3/AppData/Roaming/Microsoft/Protect/S-1-5-21-917910545-2581931138-2352614243-1000/
--sid=S-1-5-21-917910545-2581931138-2352614243-1000
--password=Welkom123$ --ntuser=/mnt/Users/os3/NTUSER.DAT
```

## Decode Database
```
./sqlite-dbx-tux64 -key ae16e208df870ca350d81d5993aa8fdb config.dbx
".backup config.db"
```
