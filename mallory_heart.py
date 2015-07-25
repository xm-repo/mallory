

import ConfigParser
import sys, time, mechanize, cookielib, random

sleep = time.sleep

#Get a new browser object
def new_browser(*args):
    # Browser
    br = mechanize.Browser()
      
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
      
    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
      
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
      
    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    return br

class QuestionPoster():

    def __init__(self, *args):
        #Thread.__init__(self)
        
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read("args.txt")

        self.questions = int(self.cfg.get("options", "questions"))
        self.is_anon = bool(int(self.cfg.get("options", "isanon")))
        self.sleeptime = int(self.cfg.get("options", "sleeptime"))

        self.USER = self.cfg.get("account", "user")
        self.PASSWORD = self.cfg.get("account", "password")

        self.q = []
        with open(self.cfg.get("files", "questions")) as f:
            for question in f:
                self.q.append(question)

        self.users = set()
        with open(self.cfg.get("files", "questions")) as f:
            for user in f:
                self.users.add(user)

    def go(self, ask = True, *args):
        while True:
            br = new_browser()
            #Open Login Page
            br.open('http://ask.fm/login')
            br.select_form(nr=0)
            br.form['login'] = self.USER
            br.form['password'] = self.PASSWORD
            br.submit()
            n = 0
            while True:
                #Open Stream
                br.open('http://ask.fm/account/stream')
                lines = br.response().readlines()
                for line in lines:
                    if 'str_profile_avatar' in line:
                        
                        tmp = line.split('href="')[1]
                        user = tmp[:tmp.find('"')]

                        if user not in self.users: 
                            with open("users.txt", "a") as f:
                                self.users.add(user)
                                f.write(user + "\n")
                        else:
                            continue

                        if not ask: 
                            continue

                        qid = random.randint(0, len(self.q) - 1)
                        for i in range(self.questions):
                            
                            qid = (qid + 100) % (len(self.q) - 1)
                            
                            br.open('http://ask.fm' + user)
                            br.select_form(nr=1)
                            br.form['question[question_text]'] = self.q[qid]
                            control = br.find_control(type="checkbox").items[0]
                            if control.disabled == False:
                                control.selected = self.is_anon
                            br.submit()
                            
                            n += 1
                            sys.stdout.write("\r" + "Questions: " + str(n))
                            sys.stdout.flush()
                            
                            for i in range(self.sleeptime):
                                sys.stdout.write("\r" + " " * 100 + "\r" + "Questions: " + str(n) + ' (' + str(self.sleeptime - i) + ')')
                                sys.stdout.flush()
                                sleep(1)
                            sys.stdout.write("\r" + " " * 100 + "\r" + "Questions: " + str(n) + ' (' + time.strftime("%H:%M:%S") + '?)')
                            sys.stdout.flush()
