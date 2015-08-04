

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

#monkey patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection

cfg = ConfigParser.ConfigParser()
cfg.read("args.txt")

sys.stdout.write("\rTor: launching")
sys.stdout.flush()

#Initializes a tor process. This blocks until initialization completes or we error out
try:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    stem.process.launch_tor() 
    signal.signal(signal.SIGINT, signal.SIG_DFL)
except Exception as e:
    sys.stdout.write("\r" + " " * 100 + "\r" + "Tor: problems \n")
    sys.stdout.flush()
    sys.exit(0)

sys.stdout.write("\r" + " " * 100 + "\r" + "Tor: ready")
sys.stdout.flush()

qp = mallory_heart.QuestionPoster()
while True:

    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, cfg.get("tor", "ip"), int(cfg.get("tor", "port")), True)
        print('q')
        socket.socket = socks.socksocket
        qp.go()
    
    except KeyboardInterrupt as e:
        print("\nGoodbye!")
        socks.setdefaultproxy()
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  # pr ovide the password here if you set one
            tor_controller.signal(stem.Signal.SHUTDOWN)
        sys.exit(0)
    
    except Exception as e:      
        socks.setdefaultproxy()
        with Controller.from_port(port = 9051) as tor_controller:
            tor_controller.authenticate()  # provide the password here if you set one
            if tor_controller.is_newnym_available():
                tor_controller.signal(stem.Signal.NEWNYM)
                time.sleep(tor_controller.get_newnym_wait())
