
import curses
from os import system
from stem.control import Controller, EventType
import ConfigParser
import stem.process
import socks, socket
import signal
import sys, time, mechanize, cookielib, random
import mallory_heart

stdscr = curses.initscr()
#curses.curs_set(0)

def CUI_update(op, msg=None):
    stdscr.move(op, 0)
    stdscr.clrtoeol()
    stdscr.addstr(msg)
    stdscr.refresh()

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

#monkey patch the socket module to make it use TOR
socket.socket = socks.socksocket
socket.create_connection = create_connection

cfg = ConfigParser.ConfigParser()
cfg.read("args.txt")

CUI_update(0, "Tor: launching")

try:
    signal.signal(signal.SIGINT, signal.SIG_IGN)  #disable sigint for tor process, so we can shutdown it 
    #Initializes a tor process. 
    stem.process.launch_tor() 
    signal.signal(signal.SIGINT, signal.SIG_DFL)  #enable sigint again
except Exception as e:
    CUI_update(0, "Tor: problems")
    
    system("sync")
    curses.endwin()
    sys.exit(0)

CUI_update(0, "Tor: ready")

qp = mallory_heart.QuestionPoster(CUI_update)  #question poster - main worker
while True:
    
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, cfg.get("tor", "ip"), int(cfg.get("tor", "port")))  #TOR socks proxy
        qp.go()
    
    except KeyboardInterrupt as e:  #shutdown TOR and exit on ^C (sigint)
        socks.setdefaultproxy()  #default proxy to interact with TOR
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  #provide the password here if you set one
            tor_controller.signal(stem.Signal.SHUTDOWN)
        
        system("sync")
        curses.endwin()
        sys.exit(0)
    
    except Exception as e:  #change ip when errors occured      
        CUI_update(3, msg="@@Last error@@" + str(e))
        socks.setdefaultproxy() #default proxy to interact with TOR
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  #provide the password here if you set one
            CUI_update(1, "{:,}".format(int(tor_controller.get_info('traffic/read')) / 10**6) + " Mb" + 
                " / " + "{:,}".format(int(tor_controller.get_info('traffic/written')) / 10**6) + " Mb")
            if tor_controller.is_newnym_available():
                tor_controller.signal(stem.Signal.NEWNYM)
                time.sleep(tor_controller.get_newnym_wait())
                CUI_update(0, "Tor: NEWNYM" + ' (' + time.strftime("%H:%M:%S") + ')')
