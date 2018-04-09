# Cloud-Service-Crawler
This repository will hold all of the code for my project with Joao Marques


## Install

Created for Python 2.7:

```
apt-get install openssl libssl-dev swig swig3.0 python2.7 python-setuptools python-pip ssdeep python-ssdeep
pip2 install -r Script/requirements.txt
chmod +x Script/working_binaries/Dropbox*
```

## Usage

Run crawler.py in the Script folder:

```
usage: python crawler.py (-f FILE | -d DIR) -t TARGET

This script is a cloud service crawler that finds commonly used cloud 
services
in a path.

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Specify user
  -m MOUNT_POINT, --mount-point MOUNT_POINT
                        Specify Mountpoint of the filesystem
  -s SCAN_DIRECTORY, --scan-directory SCAN_DIRECTORY
                        Specify directories to scan
  -v, --verbose         Show debugging information
  --version             show program's version number and exit

Required:
  -f FILE, --file FILE  Path to hashes file
  -d DIR, --dir DIR     Path to directory containing hashes files
```
