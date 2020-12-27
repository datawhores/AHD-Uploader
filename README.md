TODO

* Add qbit

* Add deluge

* Add Transmission

* ADD Template

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
    
    -- media:Can be a path or directory to upload torrents from
    -- client:name of client
    -- clienturl: url for the client 

## [Client]
    
    -- client
         rtorrent; url to scgi or xmlrpc
         qbit
         transmission
         deluge

    -- clientpass:For clients that need passwords forauth
    -- clientuser: For clients that need usernames for auth
    -- clientlabel: Naming my differ depending on client, this is the label,category,   etc   that your torrent will be added as in the client


## [AHD Auth]
    
    -- passkey: AHD passkey
    -- cookies : A Cookie file in .txt format, not json
    -- uid :your user id, used for getting lastest upload

## [Torrent]
    
    All optional
    
    -- numscreens : optional argument to change how many screens shots, default is 9
    -- batchmode : if turned off, and --media is passed a directory. That directory will be treated as one upload


    ***
    These upcoming parameters should not be changed at the moment in batchmode
    As they will not reset after the first upload. 
    
    --imdb
    --mediatype
    --codec
    --group
    --type

    ***


 ## [Programs]  
    All optional
    
    -- wget : optional argument to change path to wget, programs comes with binary
    -- dottorrent : optional argument to change path to dottorent, programs comes with binary
    -- oxipng : optional argument to change path to oxipng, programs comes with binary
    -- mtn : optional argument to change path to mtn, programs comes with binary
    -- font : optional argument to change the ttf font file. Program comes with it own. Used for screenshots

# Examples
    *Anything in brackets is to replace by user value
## Rtorrent
`ahd_uploader.py --client rtorrent --clienturl <url> --passkey <passkey> --cookie <filepath> --media <path> --uid <uid>`
    optional
    * --clientcat

## Watchdir
`ahd_uploader.py --client <path> --passkey <passkey> --cookie <file> --media  <"path">      --uid  <"uid">`
## Config
* Please make sure your config is filled with all required info, for example Rtorrent needs all the paramters from the example. The rest are unneeded/optional

* commandline options will replace any option in the config

`ahd_uploader.py --config <configpath>`


