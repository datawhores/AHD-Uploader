#!/usr/bin/env python3
import requests
import subprocess
from argparse import ArgumentParser
from pathlib import Path
import shutil
import json
import http.cookiejar
import os
import tempfile
from guessit import guessit
from imdb import IMDb
import pickle
import math
import sys
from bs4 import BeautifulSoup
import configparser
from requests_html import HTML
config = configparser.ConfigParser(allow_no_value=True)
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import radiolist_dialog,button_dialog,input_dialog

import re
from pymediainfo import MediaInfo
from threading import Thread
from shutil import which
import bencode
from pyrobase.parts import Bunch
from rtorrent_xmlrpc import SCGIServerProxy
import logging
import copy
from datetime import datetime
from consolemenu import SelectionMenu


if sys.platform!="win32":
   from simple_term_menu import TerminalMenu

KNOWN_EDITIONS = ["Director's Cut", "Unrated", "Extended Edition", "2 in 1", "The Criterion Collection"]

def createconfig(arguments):
    if arguments.config==None or os.path.exists(arguments.config)==False:
        ahdlogger.warn("Could not read config")
        return arguments
    try:
        configpath=arguments.config
        config.read(configpath)

    except:
        ahdlogger.warn("Error reading config")
        return arguments

    if arguments.log==None and len(config['general']['log'])!=0:
        arguments.log=config['general']['log']
    if arguments.log==None and len(config['general']['log'])==0:
        arguments.log="INFO"
    if arguments.passkey==None and len(config['api']['passkey'])!=0:
        arguments.passkey=config['api']['passkey']
    if arguments.uid==None and len(config['api']['uid'])!=0:
        arguments.uid=config['api']['uid']
    if arguments.media==None and len(config['general']['media'])!=0:
        arguments.media=config['general']['media']
    if arguments.log==None and len(config['general']['log'])!=0:
        arguments.batchmode=config['general']['batchmode']
    if arguments.batchmode==None and len(config['general']['batchmode'])==0:
        arguments.batchmode=True
    if arguments.cookies==None and len(config['api']['cookies'])!=0:
        arguments.cookies=config['api']['cookies']
    if arguments.client==None and len(config['client']['client'])!=0:
        arguments.client=config['client']['client']
    if arguments.clienturl==None and len(config['client']['clienturl'])!=0:
        arguments.clienturl=config['client']['clienturl']
    if arguments.clientcat==None and len(config['client']['clientcat'])!=0:
        arguments.clientcat=config['client']['clientcat']
    if arguments.clientuser==None and len(config['client']['clientuser'])!=0:
        arguments.clientuser=config['client']['clientuser']
    if arguments.clientpass==None and len(config['client']['clientpass'])!=0:
        arguments.clientpass=config['client']['clientpass']
    if arguments.font==None and len(config['general']['font'])==0:
        arguments.font=os.path.join(os.path.dirname(os.path.abspath(__file__)),"bin","OpenSans-Regular.ttf")
    if arguments.font==None :
        arguments.font=config['general']['font']
    if arguments.numscreens!=None :
        arguments.numscreens=int(arguments.numscreens)
    if arguments.numscreens==None and len(config['general']['numscreens'])==0:
        arguments.numscreens=9
    if arguments.numscreens==None and len(config['general']['numscreens'])!=0 :
        arguments.numscreen==int(config['general']['numscreens'])
    if arguments.mtn==None and len(config['programs']['mtn'])>0 :
        arguments.mtn=config['programs']['mtn']
    if arguments.oxipng==None and len(config['programs']['oxipng'])>0 :
        arguments.oxipng=config['programs']['oxipng']
    if arguments.dottorrent==None and len(config['programs']['dottorrent'])>0 :
        arguments.dottorrent=config['programs']['dottorrent']
    if arguments.wget==None and len(config['programs']['wget'])>0 :
        arguments.wget=config['programs']['wget']
    if arguments.fd==None and len(config['programs']['fd'])>0 :
        arguments.fd=config['programs']['fd']

        #set logger

    if arguments.log.upper() == "DEBUG":
        ahdlogger.setLevel(logging.DEBUG)
    elif arguments.log.upper() == "INFO":
        ahdlogger.setLevel(logging.INFO)
    else:
        ahdlogger.setLevel(logging.WARN)

    #This line is critical to hide crtical information
    t=copy.deepcopy(arguments)
    t.passkey=None
    t.uid=None
    ahdlogger.debug(t)
    return arguments










def get_imdb_info(path):
    details=guessit(path)
    title = details['title']
    if 'year' in details:
        title = "{} {}".format(title, details['year'])
    results = IMDb().search_movie(title)
    if len(results)==0 :
        ahdlogger.warn("Unable to find imdb")
        id = input("Enter Title or imdb(no tt) ")
        if re.search("tt",id)!=None:
            results=IMDb().get_movie(id)
        else:
            results = IMDb().search_movie(id)
    ahdlogger.debug(results)
    if isinstance(results, list)!=True:
        return results

    counter=0
    accept=False
    ahdlogger.warn("Searching for movie/TV Show on IMDB\n")
    while accept==False:
        if counter==6:
            id=input("Please Enter imdb id: ")
            id=re.sub("https://www.imdb.com/title/","",id)
            id=re.sub("tt","",id)
            id=re.sub("/","",id)
            results=IMDb().get_movie(id)
            return results
        title=results[counter]['title']
        year=str(results[counter]['year'])
        t=f"{title} {year}"
        accept = radiolist_dialog(
        values=[
            (True, "Yes"),
            (False, "No"),
        ],
        title=t,
        text="is this correct movie/tv title?",
        ).run()
        if accept==False:
            counter=counter+1
    if accept==False:
        id=input("Please Enter imdb id")
        id=re.sub("https://www.imdb.com/title/","",id)
        id=re.sub("tt","",id)
        id=re.sub("/","",id)
        results=IMDb().get_movie(id)
        return results
    return results[counter]

def create_binaries(arguments):
    print("Setting up Binaries")
    workingdir=os.path.dirname(os.path.abspath(__file__))
    if arguments.dottorrent==None:
        if which("dottorrent")!=None and len(which('dottorrent'))>0:
            arguments.dottorrent=which('dottorrent')
        else:
            dottorrent=os.path.join(workingdir,"bin","dottorrent")
            arguments.dottorrent=dottorrent
    ahdlogger.debug(f"dottorrent: {arguments.dottorrent}")
    if arguments.oxipng==None and sys.platform=="linux":
        if which("oxipng")!=None and len(which('oxipng'))>0:
            arguments.oxipng=which('oxipng')
        else:
            oxipng=os.path.join(workingdir,"bin","oxipng")
            arguments.oxipng=oxipng

    if arguments.oxipng==None and sys.platform=="win32":
       if which("oxipng.exe")!=None and len(which('oxipng.exe'))>0:
            arguments.oxipng=which('oxipng.exe')
       else:
           oxipng=os.path.join(workingdir,"bin","oxipng.exe")
           arguments.oxipng=oxipng
    ahdlogger.debug(f"oxipng: {arguments.oxipng}")

    if arguments.mtn==None and sys.platform=="linux":
        if which("mtn")!=None and len(which('mtn'))>0:
            arguments.mtn=which('mtn')
        else:
            mtn=os.path.join(workingdir,"bin","mtn")
            arguments.mtn=mtn
    if arguments.mtn==None and sys.platform=="win32":
        if which("mtn")!=None and len(which('mtn.exe'))>0:
            arguments.mtn=which('mtn.exe')
        else:
            mtn=os.path.join(workingdir,"bin","mtn-win32","bin","mtn.exe")
            arguments.mtn=mtn
    ahdlogger.debug(f"mtn: {arguments.mtn}")
    if arguments.wget==None and sys.platform=="linux":
        if  which('wget')!=None and len(which('wget'))>0:
            arguments.wget=which('wget')
        else:
            ahdlogger.warn("Please Install wget")
            quit()


    if arguments.wget==None and sys.platform=="win32":
        if which('wget.exe')!=None and len(which('wget.exe'))>0:
            arguments.wget=which('wget.exe')
        else:
            wget=os.path.join(workingdir,"bin","wget.exe")
            arguments.wget=wget
    ahdlogger.debug(f"wget: {arguments.wget}")
    if arguments.fd==None and sys.platform=="linux":
        if which('fd')!=None and len(which('fd'))>0:
            arguments.fd=which('fd')
        else:
            fd=os.path.join(workingdir,"bin","fd")
            arguments.fd=fd
    if arguments.fd==None and sys.platform=="win32":
        if which('fd.exe')!=None and len(which('fd.exe'))>0:
            arguments.fd=which('fd')
        else:
            fd=os.path.join(workingdir,"bin","fd.exe")
            arguments.fd=fd
    ahdlogger.debug(f"fd: {arguments.fd}")
def autodetect_type(path,arguments):
    imdb_info = get_imdb_info(path)
    arguments.imdb="tt"+imdb_info.movieID
    ahdlogger.debug(imdb_info)
    if imdb_info['kind'] == 'tv series':
        return 'TV-Shows'
    try:
        html = HTML(html=requests.get("https://www.imdb.com/title/tt{}".format(imdb_info.movieID)).text)
        if 'TV Special' in html.find('.subtext')[0].html:
            return 'TV-Shows'
    except:
        pass
    return 'Movies'


def autodetect_media_type(path):

    MEDIA_TYPES = ['Blu-ray', 'HD-DVD', 'HDTV', 'WEB-DL', 'WEBRip', 'DTheater', 'XDCAM', 'UHD Blu-ray']
    if re.search("HD-DVD",path,re.IGNORECASE)!=None:
        return 'HD-DVD'
    elif re.search("HDTV",path,re.IGNORECASE)!=None:
        return 'HDTV'
    elif re.search("UHD Blu-ray",path,re.IGNORECASE)!=None:
        return 'UHD Blu-ray'
    elif re.search("WEB-DL",path,re.IGNORECASE)!=None:
        return 'WEB-DL'
    elif re.search("WEBRip",path,re.IGNORECASE)!=None:
        return 'WEBRip'
    elif re.search("Blu-ray",path,re.IGNORECASE)!=None:
        return 'Blu-ray'
    elif re.search("DTheater",path,re.IGNORECASE)!=None:
        return 'DTheater'
    elif re.search("XDCAM",path,re.IGNORECASE)!=None:
        return 'XDCAM'
    confirm=False
    while confirm==False:
        upstring=os.path.basename(path) +": What Type of Upload Do you Have"
        value= radiolist_dialog(
        values=[
            ("Blu-ray", "Blu-ray"),
            ("HD-DVD", "HD-DVD"),
            ("HDTV", "HDTV"),
            ("WEB-DL", "WEB-DL"),
            ("WEBRip", "WEBRip"),
            ("DTheater", "DTheater"),
            ("XDCAM", "XDCAM"),
            ("UHD Blu-ray", "UHD Blu-ray"),
        ],
        title="Type",
        text=upstring,
        ).run()
        if value==None:
            quit()
        confirm = button_dialog(
            title=value,
            buttons=[("Correct?", True), ("No", False)],
        ).run()
    return value





def autodetect_codec(path):
    if re.search("h.264",path,re.IGNORECASE)!=None and (re.search("blu",path,re.IGNORECASE)!=None or re.search("web",path,re.IGNORECASE)==None ):
        return 'h.264 Remux'
    elif re.search("h.265",path,re.IGNORECASE)!=None and (re.search("blu",path,re.IGNORECASE)!=None or re.search("web",path,re.IGNORECASE)==None):
        return 'x264'
    elif re.search("x265",path,re.IGNORECASE)!=None:
        return 'x265'
    elif re.search("x264",path,re.IGNORECASE)!=None:
        return 'x264'
    elif re.search("VC-1 Remux",path,re.IGNORECASE)!=None:
        return 'VC-1 Remux'
    elif re.search("MPEG2 Remux",path,re.IGNORECASE)!=None:
        return 'MPEG2 Remux'
    confirm=False
    while confirm==False:
        upstring=os.path.basename(path)+"\n What is the codec of the Upload"
        value= radiolist_dialog(
        values=[
            ("x264", "x264"),
            ("h.264 Remux", "h.264 Remux"),
            ("x265", "x265"),
            ("h.265 Remux", "h.265 Remux"),
            ("VC-1 Remux", "VC-1 Remux"),
            ("MPEG2 Remux", "MPEG2 Remux"),
        ],
        title="Type",
        text=upstring,
        ).run()
        if value==None:
            quit()
        confirm = button_dialog(
            title=value,
            buttons=[("Correct?", True), ("No", False)],
        ).run()
    return value


def autodetect_group(path):
    g = guessit(Path(path).name)
    return g.get('release_group',"UNKNOWN")


def preprocessing(path, arguments):
    print("Detecting Upload INFO")
    assert Path(path).exists()
    if arguments.type == 'AUTO-DETECT':
        arguments.type= autodetect_type(path,arguments)
    if arguments.imdb == 'AUTO-DETECT':
        arguments.imdb= "tt"+get_imdb_info(path).movieID
    ahdlogger.debug(f"imdb: {arguments.imdb}")
    if arguments.group == 'AUTO-DETECT':
        arguments.group = autodetect_group(path)
    ahdlogger.debug(f"group: {arguments.group}")
    if arguments.mediatype == 'AUTO-DETECT':
        arguments.mediatype = autodetect_media_type(path)
    ahdlogger.debug(f"mediatype: {arguments.mediatype}")
    if arguments.codec == 'AUTO-DETECT':
        arguments.codec = autodetect_codec(path)
        if arguments.mediatype == 'WEB-DL':
            if arguments.codec == 'x264' or 'H.264' in Path(path).name:
                arguments.codec = 'h.264 Remux'
            if arguments.codec == 'x265' or 'H.265' in Path(path).name or 'HEVC' in Path(path).name:
                arguments.codec = 'h.265 Remux'
    ahdlogger.debug(f"codec: {arguments.codec}")
    if arguments.type == 'Movies':
        if 'AMZN' in Path(path).name:
            arguments.specialedition = 'Amazon'

        if 'Netflix' in Path(path).name or '.NF.' in Path(path).name:
            arguments.specialedition = 'Netflix'
    ahdlogger.debug(f"specialedition: {arguments.specialedition}")


def create_torrent(path,torrent,dottorrent):
    print("Creating Torrent For Upload")
    p = subprocess.run([sys.executable,dottorrent, '-s', '16M', '-p',path, torrent], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ahdlogger.debug(p.stdout)
    ahdlogger.debug(f"Torrent Size: {os.path.getsize(torrent)}")
    if p.returncode != 0:
        raise RuntimeError("Error creating torrent: {}".format(p.stdout))


def get_mediainfo(path):
    print("Getting Mediainfo")
    media_info = MediaInfo.parse(path,output="STRING")
    media_info=media_info.encode(encoding='utf8')
    media_info=media_info.decode('utf8', 'strict')
    ahdlogger.debug(media_info)
    return media_info


def take_screenshots(path,dir,numscreens,font,mtn,oxipng):
    print("Taking Screenshots")
    media_info = MediaInfo.parse(path)
    for track in media_info.tracks:
        if track.track_type == 'Video':
            interval=float(track.duration)/1000
            interval=math.floor(interval/numscreens)
            ahdlogger.debug(f"ScreenShot Interval: {interval} steps")
            break
    t=subprocess.run([mtn,'-n','-z','-f',font,'-o','.png','-w','0','-P','-s',str(interval),'-I',path,'-O',dir.name],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #delete largest pic
    ahdlogger.debug(t.stdout)
    ahdlogger.debug(f"File Names Images {os.listdir(dir.name)}")
    max=0
    delete=""
    for filename in os.listdir(dir.name):
       filename=os.path.join(dir.name,filename)
       temp=os.path.getsize(filename)
       if(temp>max):
            max=temp
            delete=filename
    ahdlogger.debug(f"Deleting the thumbnail image: {delete} ")
    os.remove(delete)
    for filename in os.listdir(dir.name):
        filename=os.path.join(dir.name,filename)
        ahdlogger.debug(f"Old Size: {filename} {os.path.getsize(filename)} bytes")
        t=subprocess.run([oxipng,'-o','6','strip safe',filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ahdlogger.debug(f"New Size: {filename} {os.path.getsize(filename)}")


def upload_screenshots(gallery_title, dir, key):
    print("Uploading screenshots")
    bbcode=""
    try:
        for file in os.scandir(dir.name):
            file=os.path.join(dir.name,file.name)
            data_payload = {'apikey': key, 'galleryid': 'new', 'gallerytitle': gallery_title}
            files_payload = [('image[]', (os.path.basename(file),open(file, 'rb')))]
            t=requests.post('https://img.awesome-hd.me/api/upload', data=data_payload,files=files_payload)
            ahdlogger.debug(f"uploaded {file} {t.status_code}")
            if t!=None:
                ahdlogger.debug(f"{t.json()}\n")
                bbcode=bbcode+t.json()['files'][0]['bbcode']
            else:
                continue
        ahdlogger.debug(bbcode)
        return bbcode
    except:
        return bbcode



def create_upload_form(arguments,inpath,torrentpath):
    print("Starting UploadForm Process")
    t=datetime.now().strftime("%m.%d.%Y_%H%M")
    ahdlogger.warn(f"Creating Form {t}")
    if os.path.isdir(inpath):
        single_file=subprocess.run([arguments.fd,'.',inpath,'--max-results','1','-e','.mkv'],stdout=subprocess.PIPE).stdout.decode("utf-8")
        single_file=single_file.rstrip()
        single_file=f'{single_file}'




    else:
        single_file=inpath
    ahdlogger.debug(f"single file: {single_file}")
    ahdlogger.debug(f"Uploading Path: {inpath}")
    imgdir = tempfile.TemporaryDirectory()
    release_info = Thread(target = take_screenshots, args = (single_file,imgdir,arguments.numscreens,arguments.font,arguments.mtn,arguments.oxipng))
    release_info.start()
    torrent=Thread(target = create_torrent, args = (inpath,torrentpath,arguments.dottorrent))
    torrent.start()
    preprocessing(single_file, arguments)
    torrent.join()
    release_info.join()

    arguments.title=os.path.basename(single_file)



    form = {'submit':'true',
            'nfo_input': "",
            'type': arguments.type,
            'imdblink': arguments.imdb,
            'file_media': "",
            'pastelog': get_mediainfo(single_file),
            'group': arguments.group,
            'remaster_title': "Director's Cut",
            'othereditions': "",
            'media': arguments.mediatype,
            'encoder': arguments.codec,
            'release_desc': upload_screenshots(arguments.title,imgdir,arguments.passkey)}


    if arguments.group == 'UNKNOWN':
        form['unknown_group'] = 'on'
        form['group'] = ''
    if arguments.userrelease:
        form['user'] = 'on'
    if arguments.specialedition:
        form['remaster'] = 'on'
        if arguments.specialedition not in KNOWN_EDITIONS:
            form['othereditions'] = arguments.specialedition
            form['unknown'] = 'on'
        else:
            form['remaster_title'] = arguments.specialedition

    ahdlogger.debug(form)
    return form


def upload_command(arguments,form,torrent):
    print("Uploading to AHD")
    assert Path(arguments.cookies).exists() and not Path(arguments.cookies).is_dir()
    r = upload_form(arguments,form,torrent)
    if r!=None and r.status_code == 200:
        pass
    else:
        raise RuntimeError("Something went wrong while uploading! It's recommended to check AHD to verify that you"
                           "haven't uploaded a malformed or incorrect torrent.")
    try:
        return getlink(arguments)
    except:
        return None


def upload_form(arguments, form,torrent):
    cj = http.cookiejar.MozillaCookieJar(arguments.cookies)
    cj.load()
    files={'file_input': open(torrent,'rb')}
    try:
        t=requests.post("https://awesome-hd.me/upload.php",
                         cookies=requests.utils.dict_from_cookiejar(cj),
                         data=form,files=files,timeout=120)
    except:
        ahdlogger.info("Upload PostRequest Failed")
        return None
    soup = BeautifulSoup(t.text, 'html.parser')
    soup=soup.title
    ahdlogger.debug(f"Succesful Upload? {soup}")
    return t


def getlink(arguments):
    #get the last upload from profile
    cj = http.cookiejar.MozillaCookieJar(arguments.cookies)
    cj.load()
    t=requests.post(f"https://awesome-hd.me/torrents.php?type=uploaded&userid={arguments.uid}",
                         cookies=requests.utils.dict_from_cookiejar(cj),
                         timeout=120)
    soup = BeautifulSoup(t.text, 'html.parser')
    ahdlogger.debug(f"Getting Link from  User Profile? {soup.title}")
    try:
        table=soup.find_all("div",class_="linkbox")[0].next_sibling.next_sibling
    except:
        ahdlogger.warn("Error Getting Torrent Table")
        return
    try:
        link=table.find_all("tr")[1].find("a")["href"]
    except:
        ahdlogger.warn("Error parsing link from Torrent Table")
        return
    return "https://awesome-hd.me/"+link


def download_torrent(arguments,ahd_link,path):
    print("Downloading Torrent to client")
    cookie=arguments.cookies
    wget=arguments.wget
    client=arguments.client
    if client not in ["rtorrent","qbit","deluge","transmission"]:
        name="".join([arguments.title,".torrent"])
        torrentpath=os.path.join(client,name)
        ahdlogger.info(torrentpath)
        try:
            t=subprocess.run([wget,'--load-cookies',cookie,ahd_link,'-O',torrentpath],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            ahdlogger.debug(f"Downloading Final Torrent -No Fast Resume Data added :{t.stdout}")
        except:
            ahdlogger.warn("error downloading torrent please get directly from AHD")
    if client=="rtorrent":
        temptor=os.path.join(tempfile.gettempdir(), os.urandom(24).hex()+".torrent")
        t=subprocess.run([wget,'--load-cookies',cookie,ahd_link,'-O',temptor],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #important line remove private infromation from download link
        downloadurl=re.sub(arguments.passkey,"",t.stdout)
        ahdlogger.debug(f"Downloading Temp Torrent:{downloadurl}")
        metainfo=bencode.bread(temptor)
        resumedata = add_fast_resume(metainfo, path)
        ahdlogger.info(f"resume date added?: {bencode.encode(resumedata)!=metainfo}")
        if bencode.encode(resumedata)!=metainfo:
            bencode.bwrite(resumedata,temptor)
        clienturl=re.sub("unix","scgi",arguments.clienturl)
        server = SCGIServerProxy(clienturl)
        if arguments.clientcat!=None:
            server.load.start_verbose("",temptor,f"d.directory_base.set={path}",f"d.custom1.set={arguments.clientcat}")
        else:
            server.load.start_verbose("",temptor,f"d.directory_base.set={path}")


def add_fast_resume(meta, datapath):
    """ Add fast resume data to a metafile dict.
    """
    # Get list of files
    files = meta["info"].get("files", None)
    single = files is None
    if single:
        if os.path.isdir(datapath):
            datapath = os.path.join(datapath, meta["info"]["name"])
        files = [Bunch(
            path=[os.path.abspath(datapath)],
            length=meta["info"]["length"],
        )]

    # Prepare resume data
    resume = meta.setdefault("libtorrent_resume", {})
    resume["bitfield"] = len(meta["info"]["pieces"]) // 20
    resume["files"] = []
    piece_length = meta["info"]["piece length"]
    offset = 0

    for fileinfo in files:
        # Get the path into the filesystem
        filepath = os.sep.join(fileinfo["path"])
        if not single:
            filepath = os.path.join(datapath, filepath.strip(os.sep))

        # Check file size
        if os.path.getsize(filepath) != fileinfo["length"]:
            raise OSError(errno.EINVAL, "File size mismatch for %r [is %d, expected %d]" % (
                filepath, os.path.getsize(filepath), fileinfo["length"],
            ))

        # Add resume data for this file
        resume["files"].append(dict(
            priority=1,
            mtime=int(os.path.getmtime(filepath)),
            completed=(offset+fileinfo["length"]+piece_length-1) // piece_length
                     - offset // piece_length,
        ))
        offset += fileinfo["length"]

    return meta



if __name__ == '__main__':
    workingdir=os.path.dirname(os.path.abspath(__file__))

    try:
        os.mkdir(os.path.join(workingdir,"Logs"))
    except:
        pass
    #Create Logger
    ahdlogger = logging.getLogger('AHD')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    filehandler=logging.FileHandler(os.path.join(workingdir,"Logs","ahdupload.logs"))
    filehandler.setFormatter(formatter)
    ahdlogger.addHandler(filehandler)
    parser = ArgumentParser()
    parser.add_argument("--media",default=None)
    parser.add_argument("--config",default=None)
    parser.add_argument("--passkey",default=None)
    parser.add_argument("--cookies",default=None)
    parser.add_argument("--uid",default=None)
    parser.add_argument("--client",default=None)
    parser.add_argument("--clienturl",default=None)
    parser.add_argument("--clientcat",default=None)
    parser.add_argument("--clientuser",default=None)
    parser.add_argument("--clientpass",default=None)
    parser.add_argument("--txtoutput",default=None)
    parser.add_argument("--font",default=None)
    parser.add_argument("--imdb",default="AUTO-DETECT")
    parser.add_argument("--mediatype",default="AUTO-DETECT")
    parser.add_argument("--codec",default="AUTO-DETECT")
    parser.add_argument("--group",default="AUTO-DETECT")
    parser.add_argument("--type",default="AUTO-DETECT")
    parser.add_argument("--userrelease",default=None)
    parser.add_argument("--specialedition",default=None)
    parser.add_argument("--numscreens",default=None)
    parser.add_argument("--oxipng",default=None)
    parser.add_argument("--dottorrent",default=None)
    parser.add_argument("--wget",default=None)
    parser.add_argument("--mtn",default=None)
    parser.add_argument("--fd",default=None)
    parser.add_argument("--batchmode",default=None)
    parser.add_argument("--log",default=None)
    arguments = parser.parse_args()
    arguments=createconfig(arguments)
    torrentpath=os.path.join(tempfile.gettempdir(), os.urandom(24).hex()+".torrent")
    create_binaries(arguments)
    keepgoing = "Yes"
    #setup batchmode
    if os.path.isdir(arguments.media) and (arguments.batchmode==True or  arguments.batchmode=="True"):
        choices=sorted(os.listdir(arguments.media))


    #single upload
    else:
        form=create_upload_form(arguments,arguments.media,torrentpath)
        ahd_link=upload_command(arguments,form,torrentpath)
        if ahd_link!=None:
            print(ahd_link)
            download_torrent(arguments,ahd_link,arguments.media)
        else:
            ahdlogger.warn("Was Not able to get torrentlink")
        quit()



    #batchmode
    while keepgoing=="Yes" or keepgoing=="yes" or keepgoing=="Y" or keepgoing=="y"  or keepgoing=="YES":
        if sys.platform!="win32":
            menu = TerminalMenu(choices)
            menu_entry_index = menu.show()
        else:
            menu_entry_index = SelectionMenu.get_selection(choices)


        if menu_entry_index>= (len(choices)):
            quit()
        try:
            path=choices[int(menu_entry_index)]

        except:
            ahdlogger.warn("Please Enter a Valid Value")
            continue
        path=os.path.join(arguments.media,path)
        print("\n")
        form=create_upload_form(arguments,path,torrentpath)
        ahd_link=upload_command(arguments,form,torrentpath)
        if ahd_link!=None:
            print(ahd_link)
            download_torrent(arguments,ahd_link,path)
        else:
            ahdlogger.warn("Was Not able to get torrentlink")
        keepgoing=input("Upload Another File: ")
