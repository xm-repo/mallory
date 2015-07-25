#Libs needed
#socksipy
#pycurl
#Mechanize - http://wwwsearch.sourceforge.net/mechanize/
#Stem - https://stem.torproject.org

#get some questions from http://www.yensa.com

#import pycurl
import atexit
import os, signal, subprocess
from stem.control import Controller
import ConfigParser
import stem.process
import socks, socket
import sys, threading, time, mechanize, cookielib, random
import mallory_heart

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

#monkey patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection

cfg = ConfigParser.ConfigParser()
cfg.read("args.txt")

sys.stdout.write("\rTor: launching")
sys.stdout.flush()
#Initializes a tor process. This blocks until initialization completes or we error out
stem.process.launch_tor()
sys.stdout.write("\r" + " " * 100 + "\r" + "Tor: ready")
sys.stdout.flush()

while True:

    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, cfg.get("tor", "ip"), int(cfg.get("tor", "port")), True)
        socket.socket = socks.socksocket
        qp = mallory_heart.QuestionPoster()
        qp.go()
    
    except KeyboardInterrupt:
        print("\nGoodbye!")
        socks.setdefaultproxy()
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  # pr ovide the password here if you set one
            tor_controller.signal(stem.Signal.SHUTDOWN)
        sys.exit(0)
    
    except Exception as e:
        print("\nProblems") 
        print(e)      
        socks.setdefaultproxy()
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  # provide the password here if you set one
            if tor_controller.is_newnym_available():
                print("NEWNYM")
                tor_controller.signal(stem.Signal.NEWNYM)
                time.sleep(tor_controller.get_newnym_wait())
