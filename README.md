TODO

* Add qbit

* Add deluge

* Add Transmission

* ADD Template System

* ADD ability to manually enter parameters for torrents i.e change category. While in batchmode




# Install
## Clone the repository
git clone https://github.com/excludedBittern8/AHD-Uploader

cd AHD-Uploader

## Creating a virtual enviroment
A Virtual environment is recommended. Please Make sure you are on python3 and NOT python 2

##### install virtualenv
On macOS and Linux:

python3 -m pip install --user virtualenv

On Windows:

py -m pip install --user virtualenv

##### create the virtualenv
On Linux:

python3 -m venv venv

On Windows:
python3 -m venv venv
or
py -m venv venv
##### Add required modules
On Linux:

./venv/bin/pip3 install -r requirements.txt

On Windows:

venv\Scripts\pip3.exe install -r requirements.txt

##### running python from venv
On Linux
/venv/bin/python3

on Windows
venv\Scripts\python


# Parameters


## [general]
    
-- media:Can be a path or directory to upload torrents from. 
    
  >   If a directory batchmode will start. Which will non-recursivly scan the drive, and output the result as menu. Where you can select the file/folder to upload. Non-recursive meaning what you see if you click the directory once. If you want to upload an entire folder as one upload, even if it has subfolders. --batchmode False will work

optional
    
--batchmode:Upload all elements in a directory
--config:Pass arguments via a file instead of commandline. example.config is provided

--log:**This does not take a path.** Valid inputs for this are debug,warn,info. In order of output descending debug,info, warn. If you having issues please run the program with 
`--log debug` it will provide information about the process which will tell 

## [Client]

- -- client:name of client
    - rtorrent
    - qbit
    - transmission
    - deluge
    - watchdir:If  client is not any of the above values, then it is a "watchdir". To properly use pass the full path to the directory you want to upload to

- -- clientpass:For clients that need passwords forauth
- -- clientuser: For clients that need usernames for auth
- -- clientcat: Naming my differ depending on client, this is the label,category,   etc   that your torrent will be added as in the client
- -- clienturl: url for the client 


## [AHD Auth]
 These are all required to upload, autoretrive upload link  

- -- passkey: AHD passkey
- -- cookies : A cookie file in .txt format, not json
- -- uid :your user id, used for getting lastest upload

## [Torrent]
    
> These parameters control the final upload. Most can be changed after upload. \
Other then imdb,screenshots. They are all optional
    
- -- numscreens : optional argument to change how many screens shots, default is 9

 
> These upcoming parameters should not be changed at the moment in batchmode
> As they will not reset after the first upload. 
>     
> - --imdb
> - --mediatype
> - --codec
> - --group
> - --type
> - --userrelease
> - --specialedition




 ## [Programs]  
> These control the paths to the required programs. Only change if you want to use your own binaries
On windows please enter the fullpath. You can usually find that by 
1. Enter python 
2. from sys import which
3. which(program)

There is some combability issues with using path and windows, that causes issues with other commands in the program
    
- -- wget : optional argument to change path to wget, programs comes with binary
- -- dottorrent : optional argument to change path to dottorent, programs comes with binary
- -- oxipng : optional argument to change path to oxipng, programs comes with binary
- -- mtn : optional argument to change path to mtn, programs comes with binary
- -- font : optional argument to change the ttf font file. Program comes with it own. Used for screenshots

# Examples
    *Anything in brackets is to replace by user value
## Rtorrent
`ahd_uploader.py --client rtorrent --clienturl <url> --passkey <passkey> --cookie <filepath> --media <path> --uid <uid>`
    
    optional
    - --clientcat

## Watchdir
`ahd_uploader.py --client <path> --passkey <passkey> --cookie <file> --media <path> --uid  <uid>`
## Config
* Please make sure your config is filled with all required info, for example rtorrent needs all the paramters from the rtorrent example. For Parameter Usage Please Go to the Parameter section

* commandline options will replace any option in the config

`ahd_uploader.py --config <configpath>`


