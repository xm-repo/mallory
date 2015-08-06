

from stem.control import Controller
import ConfigParser
import stem.process
import socks, socket
import signal
import sys, time, mechanize, cookielib, random
import mallory_heart

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

#monkey patch the socket module to make it use TOR
socket.socket = socks.socksocket
socket.create_connection = create_connection

cfg = ConfigParser.ConfigParser()
cfg.read("args.txt")

sys.stdout.write("\rTor: launching")
sys.stdout.flush()

try:
    signal.signal(signal.SIGINT, signal.SIG_IGN)  #disable sigint for tor process, so we can shutdown it 
    #Initializes a tor process. 
    stem.process.launch_tor() 
    signal.signal(signal.SIGINT, signal.SIG_DFL)  #enable sigint again
except Exception as e:
    sys.stdout.write("\r" + " " * 100 + "\r" + "Tor: problems \n")
    sys.stdout.flush()
    sys.exit(0)

sys.stdout.write("\r" + " " * 100 + "\r" + "Tor: ready")
sys.stdout.flush()

qp = mallory_heart.QuestionPoster()  #question poster - main worker
while True:

    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, cfg.get("tor", "ip"), int(cfg.get("tor", "port")))  #TOR socks proxy
        qp.go()
    
    except KeyboardInterrupt as e:  #shutdown TOR and exit on ^C (sigint)
        print("\nGoodbye!")
        socks.setdefaultproxy()  #default proxy to interact with TOR
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  #provide the password here if you set one
            tor_controller.signal(stem.Signal.SHUTDOWN)
        sys.exit(0)
    
    except Exception as e:  #change ip when errors occured      
        socks.setdefaultproxy() #default proxy to interact with TOR
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  #provide the password here if you set one
            if tor_controller.is_newnym_available():
                tor_controller.signal(stem.Signal.NEWNYM)
                time.sleep(tor_controller.get_newnym_wait())
