#! /usr/bin/env python3
import requests
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
import pendulum
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
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import button_dialog
import re
from pymediainfo import MediaInfo
from threading import Thread
from shutil import which
import bencode
from pyrobase.parts import Bunch
from rtorrent_xmlrpc import SCGIServerProxy

if sys.platform!="win32":
   from simple_term_menu import TerminalMenu

KNOWN_EDITIONS = ["Director's Cut", "Unrated", "Extended Edition", "2 in 1", "The Criterion Collection"]

def createconfig(arguments):
    if arguments.config==None or os.path.exists(arguments.config)==False:
        print("Could not read config ")
        return arguments
    try:
        configpath=arguments.config
        config.read(configpath)

    except:
        print("Error reading config")
        return arguments

    if arguments.passkey==None and len(config['api']['passkey'])!=0:
        arguments.passkey=config['api']['passkey']
    if arguments.uid==None and len(config['api']['uid'])!=0:
        arguments.uid=config['api']['uid']
    if arguments.media==None and len(config['general']['media'])!=0:
        arguments.media=config['general']['media']
    if arguments.batchmode==None and len(config['general']['batchmode'])!=0:
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
        arguments.numscreen=9
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
    return arguments










def get_imdb_info(path):
    details=guessit(path)
    title = details['title']
    if 'year' in details:
        title = "{} {}".format(title, details['year'])
    results = IMDb().search_movie(title)
    if len(results)==0 :
        print("Unable to find imdb")
        id = input("Enter Title or imdb(no tt) ")
        if re.search("tt",id)!=None:
            results=IMDb().get_movie(id)
        else:
            results = IMDb().search_movie(id)
    if isinstance(results, list)!=True:
        return results

    counter=0
    accept=False
    print("Searching for movie/TV Show on IMDB","\n")
    while accept!="True"and accept!="Y" and accept!="Yes" and accept!="YES" and accept!="y" and counter<len(results):
       if counter==6:
           print("correct title not found")
           id=""
           while len(id)==0:
               id = input("Enter imdb(no tt) ")

           results=IMDb().get_movie(id)
           return results
       print(results[counter]["title"]," ",results[counter]["year"])
       accept=input(" is this Search result correct?:")
       if len(accept)==0 or accept=="N" or accept=="No" or accept=="n" or accept=="NO":
            counter=counter+1
    return results[counter]
    if accept!="True" or  accept!="Y" or accept!="Yes" or accept!="YES" or accept!="y":
       print("correct title not found")
       id=""
       while len(id)==0:
           id = input("Enter imdb(no tt) ")
       results=IMDb().get_movie(id)
       return results
    return results[counter]

def create_binaries(arguments):
    workingdir=os.path.dirname(os.path.abspath(__file__))
    if arguments.dottorrent==None:
        if which("dottorrent")!=None and len(which('dottorrent'))>0:
            arguments.dottorrent=which('dottorrent')
        else:
            dottorrent=os.path.join(workingdir,"bin","dottorrent")
            arguments.dottorrent=dottorrent

    if arguments.oxipng==None:
        if which("oxipng")!=None and len(which('oxipng'))>0:
            arguments.oxipng=which('oxipng')
        else:
            oxipng=os.path.join(workingdir,"bin","oxipng")
            arguments.oxipng=oxipng
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

    if arguments.wget==None and sys.platform=="linux":
        if len(which('wget'))>0:
            arguments.wget=which('wget')
        else:
            print("Please Install wget")
            quit()


    if arguments.wget==None and sys.platform=="win32":
        if len(which('wget'))>0:
            arguments.wget=which('wget.exe')
        else:
            wget=os.path.join(workingdir,"bin","wget.exe")
            arguments.wget=wget


    if sys.platform=="win32":
        arguments.shellbool=True
    if sys.platform=="linux":
        arguments.shellbool=False
def autodetect_type(path,arguments):
    imdb_info = get_imdb_info(path)
    arguments.imdb="tt"+imdb_info.movieID
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
        upstring=os.path.basename(path)+": What is the codec of Upload"
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
    assert Path(path).exists()
    imdb_info = None
    if arguments.type == 'AUTO-DETECT':
        arguments.type= autodetect_type(path,arguments)
    if arguments.imdb == 'AUTO-DETECT':
        arguments.imdb= "tt"+get_imdb_info(path).movieID

    if arguments.group == 'AUTO-DETECT':
        arguments.group = autodetect_group(path)

    if arguments.mediatype == 'AUTO-DETECT':
        arguments.mediatype = autodetect_media_type(path)

    if arguments.codec == 'AUTO-DETECT':
        arguments.codec = autodetect_codec(path)
        if arguments.mediatype == 'WEB-DL':
            if arguments.codec == 'x264' or 'H.264' in Path(path).name:
                arguments.codec = 'h.264 Remux'
            if arguments.codec == 'x265' or 'H.265' in Path(path).name or 'HEVC' in Path(path).name:
                arguments.codec = 'h.265 Remux'

    if arguments.type == 'Movies':
        if 'AMZN' in Path(path).name:
            arguments.specialedition = 'Amazon'

        if 'Netflix' in Path(path).name or '.NF.' in Path(path).name:
            arguments.specialedition = 'Netflix'



def create_torrent(path,torrent,dottorrent,shellbool):
    p = subprocess.run([sys.executable,dottorrent, '-s', '16M', '-p',path, torrent], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=shellbool)
    if p.returncode != 0:
        raise RuntimeError("Error creating torrent: {}".format(p.stdout))


def get_mediainfo(path):
    if Path(path).is_dir():
        path = next(Path(path).glob('*/')).as_posix()
    media_info = MediaInfo.parse(path,output="STRING")
    media_info=media_info.encode(encoding='utf8')
    media_info=media_info.decode('utf8', 'strict')
    return media_info


def take_screenshots(path,dir,numscreens,font,mtn,oxipng,shellbool):
    media_info = MediaInfo.parse(path)
    for track in media_info.tracks:
        if track.track_type == 'Video':
            interval=float(track.duration)/1000
            interval=math.floor(interval/numscreens)
    t=subprocess.run([mtn,'-n','-z','-f',font,'-o','.png','-w','0','-P','-s',str(interval),'-I',path,'-O',dir.name],shell=shellbool,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,)
    #delete largest pic

    max=0
    delete=""
    for filename in os.listdir(dir.name):
       filename=os.path.join(dir.name,filename)
       temp=os.path.getsize(filename)
       if(temp>max):
            max=temp
            delete=filename
    os.remove(delete)
    for filename in os.listdir(dir.name):
        subprocess.run([oxipng,'-o','6','strip safe',filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=shellbool)

def upload_screenshots(gallery_title, dir, key):
    bbcode=""
    try:
        for file in os.scandir(dir.name):
            file=os.path.join(dir.name,file.name)
            data_payload = {'apikey': key, 'galleryid': 'new', 'gallerytitle': gallery_title}
            files_payload = [('image[]', (os.path.basename(file),open(file, 'rb')))]
            t=requests.post('https://img.awesome-hd.me/api/upload', data=data_payload,files=files_payload)
            if t!=None:
                bbcode=bbcode+t.json()['files'][0]['bbcode']
            else:
                continue
        return bbcode
    except:
        return bbcode



def create_upload_form(arguments,inpath,outpath):
    if os.path.isdir(inpath):
          for entity in os.scandir(inpath):
              if re.search(".mkv",entity.name)!=None or re.search(".mp4",entity.name)!=None:
                  single_file=os.path.join(inpath,entity.name)
                  break
    else:
        single_file=inpath
    imgdir = tempfile.TemporaryDirectory()
    release_info = Thread(target = take_screenshots, args = (single_file,imgdir,arguments.numscreens,arguments.font,arguments.mtn,arguments.oxipng,arguments.shellbool))
    release_info.start()
    torrent=Thread(target = create_torrent, args = (inpath,outpath,arguments.dottorrent,arguments.shellbool))
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


    return form


def upload_command(arguments,form,torrent):
    assert Path(arguments.cookies).exists() and not Path(arguments.cookies).is_dir()
    r = upload_form(arguments,form,torrent)
    if r.status_code == 200:
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
    return requests.post("https://awesome-hd.me/upload.php",
                         cookies=requests.utils.dict_from_cookiejar(cj),
                         data=form,files=files,timeout=120)


def getlink(arguments):
    #get the last upload from profile
    cj = http.cookiejar.MozillaCookieJar(arguments.cookies)
    cj.load()
    t=requests.post(f"https://awesome-hd.me/torrents.php?type=uploaded&userid={arguments.uid}",
                         cookies=requests.utils.dict_from_cookiejar(cj),
                         timeout=120)
    soup = BeautifulSoup(t.text, 'html.parser')
    try:
        table=soup.find_all("div",class_="linkbox")[0].next_sibling.next_sibling
    except:
        print("Error Getting Torrent Table")
        return
    try:
        link=table.find_all("tr")[1].find("a")["href"]
    except:
        print("Error parsing link from Torrent Table")
        return
    return "https://awesome-hd.me/"+link


def download_torrent(arguments,ahd_link,path):
    shellbool=arguments.shellbool,
    cookie=arguments.cookies
    wget=arguments.wget
    client=arguments.client
    if client not in ["rtorrent","qbit","deluge","transmission"]:
        name="".join([arguments.title,".torrent"])
        torrentpath=os.path.join(client,name)
        try:
            subprocess.run([wget,'--load-cookies',cookie,ahd_link,'-O',torrentpath])
        except:
            print("error downloading torrent please get directly from AHD")
    if client=="rtorrent":
        temptor=os.path.join(tempfile.gettempdir(), os.urandom(24).hex()+".torrent")
        subprocess.run([wget,'--load-cookies',cookie,ahd_link,'-O',temptor])
        metainfo=bencode.bread(temptor)
        resumedata = add_fast_resume(metainfo, path)
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
    parser.add_argument("--announce",default="AUTO-DETECT")
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
    parser.add_argument("--batchmode",default=None)
    arguments = parser.parse_args()
    arguments=createconfig(arguments)
    torrentpath=os.path.join(tempfile.gettempdir(), os.urandom(24).hex()+".torrent")
    create_binaries(arguments)
    keepgoing = "Yes"
    if os.path.isdir(arguments.media) and (arguments.batchmode==True or  arguments.batchmode=="True"):
        choices=os.listdir(arguments.media)
    else:
        form=create_upload_form(arguments,arguments.media,torrentpath)
        ahd_link=upload_command(arguments,form)
        if ahd_link!=None:
            print(ahd_link)
            download_torrent(arguments,ahd_link,path)
        else:
            print("Was Not able to get torrentlink")
        quit()
    while keepgoing=="Yes" or keepgoing=="yes" or keepgoing=="Y" or keepgoing=="y"  or keepgoing=="YES":
        if sys.platform!="win32":
            menu = TerminalMenu(choices)
            menu_entry_index = menu.show()
        else:
            for (i, item) in enumerate(choices):
                index="INDEX:"+str(i)
                print('[',index,item,']',end="  ")
                if (i-1)%2==0:
                    print("\n")
            print("\n","\n")
            menu_entry_index=input("Enter the INDEX of the upload: ")
        try:
            path=choices[int(menu_entry_index)]
        except:
            print("Please Enter a Valid Value")
            continue
        path=os.path.join(arguments.media,path)
        print("\n")
        form=create_upload_form(arguments,path,torrentpath)
        ahd_link=upload_command(arguments,form,torrentpath)
        if ahd_link!=None:
            print(ahd_link)
            download_torrent(arguments,ahd_link,path)
        else:
            print("Was Not able to get torrentlink")
        keepgoing=input("Upload Another File: ")
