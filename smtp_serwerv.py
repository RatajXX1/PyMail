import socket 
import threading 
from datetime import datetime
import databasa
import config
import scanner_mailer
import authorize
import ssl


def conversation(socket_client, socket_adres):    

    connver_data = {
        "User": "",
        "Password": "",
        "Mail": None,
        "Rcpt": None,
        "Logged": False,
        "Use_mail": None,
        "Host": None,
        "Auth": None,
        "Input": False,
        "Data": b"",
        "TLS_is": False,
        "Start_tls": False,
        "Close": False,
        "msg_size": 0,
        "msg_size_wil": 0,
        "body_data": "",
        "Pipeline_mode": False
    }
    user_data = {
        "emtpty_cmd": 0,
        "Max_cmd": 2
    }
    
    def print_log(value):
        if type(value) == bytes:
            value = value.decode()
        #print(datetime.now().strftime("%H:%M:%S") + " SERWER SMTP: " + value) 
        databasa.make_smtp_log(value)


    def send_response(value):
        #print_log(value)
        socket_client.send(value.encode())
        
    def send_header():
        socket_client.send(b"220 " + config.Server_name.encode() +  b" ready\r\n")
    
    def helo(cmd):
        if len(cmd) == 2:
            #if connver_data["Auth"] == None:
            send_response("250 Hello {} \r\n".format(cmd[1]))
            connver_data["Host"] = cmd[1]
            connver_data["Auth"] = "helo"
            #else:
                #send_response("550 you already user auth state commmnad\r\n")
        else:
            send_response("500 arguments error \r\n")

    def ehlo(cmd):
        if len(cmd) == 2:
            connver_data["Host"] = cmd[1]
            connver_data["Auth"] = "ehlo"
            text = ""
            extensions = ["STARTTLS", "PIPELINING", "SIZE " + str(config.max_size_of_mails), "SMTPUTF8"] + authorize.metody_logowania
            for i,v in enumerate(extensions):
                if i == 0:
                    text += "250-"+ config.Server_name +"\r\n"
                    if len(extensions) > 1:
                        text += "250-{} \r\n".format(v)
                    else:
                        text += "250 {} \r\n".format(v)
                elif i == (len(extensions)-1):
                    text += "250 {} \r\n".format(v)
                else:
                    text += "250-{} \r\n".format(v)
            send_response(text)
        else:
            send_response("500 arguments error \r\n")
    
    def mail_from(cmd, pipelin=False):
        def check_arguments(args):
            decyzja = [None, "No reconized argumenst\r\n"]
            for x in args:
                x = x.lower()
                if x.find("size=") >= 0:
                    liczba = x[len("size="):]
                    if liczba != "" and liczba.isnumeric():
                        liczba = int(liczba)
                        if liczba <= config.max_size_of_mails:
                            if decyzja[0] != False:
                                connver_data["msg_size_wil"] = int(liczba)
                                decyzja = [True, None]
                        else:
                            decyzja = [False, "size argument is too big\r\n"]
                    else:
                        decyzja = [False, "arguments syntax error\r\n"]
                elif x.find("body=") >= 0:
                    dane = x[len("body="):]
                    if dane != "" and dane in ["8bitmime"]:
                        if decyzja[0] != False:
                            connver_data["body_data"] = dane
                            decyzja = [True, None]
                    else:
                        decyzja = [False, "argumets syntax error\r\n"]
            if decyzja[0] == None:
                decyzja[0] = False
            return decyzja
    
        if cmd[1].lower() == "from:":
            if cmd[2]:
                if cmd[2].find("@") > 0 and cmd[2].count("@") == 1:
                    if cmd[2].split("@")[1] in config.MX_domains:
                        if connver_data["Logged"] == True:
                            if connver_data["Use_mail"] == cmd[2]:
                                args = check_arguments(cmd[3:])
                                if cmd[3:]:
                                    if args[0] == False:
                                        send_response("500 " + args[1] )
                                        return
                                connver_data["Mail"] = cmd[2]
                                send_response("250 OK \r\n")
                            else:
                                send_response("500 this email is not your\r\n")
                        else:
                            send_response("550 you must first authorize to send \r\n")
                    else:
                        if cmd[3:]:
                            args = check_arguments(cmd[3:])
                            if args[0] == False:
                                send_response("500 " + args[1]) 
                                return
                        connver_data["Mail"] = cmd[2]
                        send_response("250 OK \r\n")
                else:
                    send_response("550 mail syntax error \r\n")
            else:
                send_response("500 arguments error \r\n")
        else:
            send_response("500 synatx error \r\n")

    def rcpt_to(cmd, pipelin=False):
        if cmd[1].lower() == "to:":
            if len(cmd) == 3:
                def add_mail(mail_rcpt):
                    if connver_data["Rcpt"] == None:
                        connver_data["Rcpt"] = mail_rcpt
                    else:
                        if type(connver_data["Rcpt"]) == list:
                            connver_data["Rcpt"].append(mail_rcpt)
                        else:
                            dane = connver_data["Rcpt"]
                            connver_data["Rcpt"] = [dane, mail_rcpt]
                def check_if_added(mail_rcpt):
                    if connver_data["Rcpt"] == None:
                        return True
                    else:
                        if type(connver_data["Rcpt"]) == list:
                            if mail_rcpt in connver_data["Rcpt"]:
                                return False
                            else:
                                return True
                        else:
                            if connver_data["Rcpt"] == mail_rcpt:
                                return False
                            else:
                                return True
                if cmd[2].find("@") > 0 and cmd[2].count("@") == 1 :
                    if cmd[2].split("@")[1] in config.MX_domains:
                        if databasa.check_mail_exitst(cmd[2]) == True:
                            if check_if_added(cmd[2]) == True:
                                add_mail(cmd[2])
                                send_response("250 OK \r\n")
                            else:
                                send_response("500 Mail already added\r\n")
                        else:
                            send_response("550 mailbox not exists \r\n")
                    else:
                        if connver_data["Logged"] == True:
                            if check_if_added(cmd[2]) == True:
                                add_mail(cmd[2])
                                send_response("250 OK \r\n")
                            else:
                                send_response("500 Mail already added\r\n")
                        else:
                            send_response("550 you must first authorize \r\n")
                else:
                    send_response("500 mail syntax erro \r\n")
            else:
                send_response("500 arguments error \r\n")
        else:
            send_response("500 syntax error \r\n")
    
    def data(cmd, pipelin=False):
        if connver_data["Rcpt"] != None and connver_data["Mail"] != None:
            connver_data["Input"] = True
            send_response("354 OK \r\n")
        else:
            send_response("550 need more information for sent \r\n")
    
    def exit():
        connver_data["Close"] = True
        send_response("221 serwer closed\r\n")

    def noop():
        send_response("250 OK \r\n")
    
    def starttls():
        if connver_data["TLS_is"] == False:
            send_response("220 OK \r\n")
            connver_data["Start_tls"] = True
        else:
            send_response("500 TlS already is \r\n")

    def reste_con():
        send_response("250 OK \r\n")

    def parse_req(req):
        if type(req) == bytes:
            req = req.decode()    
        for x in ["\r", "\n", "\\r", "\\n"]:
            req = req.replace(x, " ")
        if req.replace(" ", "") == "":
            return ["none"]
        for x in [">", "<"]:
            req = req.replace(x, " ")
        req = req.split(" ")
        req[0] = req[0].lower()
        tab = []
        for x in req:
            if x != "":
                tab.append(x)
        req = tab
        if connver_data["Auth"] == "ehlo":
            pipeline_cmd = ["mail", "rcpt", "data"]
            ilosci = []
            for x in pipeline_cmd:
                if x in req:
                    ilosci.append(req.index(x))
            if len(ilosci) > 1:
                connver_data["Pipeline_mode"] = True
                tab = []
                for i,x in enumerate(ilosci,1):
                    if i == len(ilosci):
                        tab.append(req[x:])
                    else:
                        tab.append(req[x:ilosci[i]])
                req = tab
        return req
        
    def check_commnad(cmd):
        if connver_data["Pipeline_mode"] == False:
            if cmd[0] == "helo":
                helo(cmd)
            elif cmd[0] == "ehlo":
                ehlo(cmd)
            elif cmd[0] == "mail":
                mail_from(cmd)
            elif cmd[0] == "rcpt":
                rcpt_to(cmd)
            elif cmd[0] == "data":
                data(cmd)
            elif cmd[0] == "quit":
               exit()
            elif cmd[0] == "noop":
                noop()
            elif cmd[0] == "rset":
                reste_con()
            elif cmd[0] == "starttls":
                starttls()
            elif cmd[0] == "auth":
                authorize.auth_set(cmd, socket_client, socket_adres, connver_data)
            else:
                send_response("500 commnand cannot reconized or not supported\r\n")
                user_data["emtpty_cmd"] += 1
                if user_data["emtpty_cmd"] > 3:
                    databasa.set_banned_ip(socket_adres[0])
                    connver_data["Close"] = True
        else:
            for x in cmd:
                if x[0] == "mail":
                    mail_from(x, pipelin=True)
                elif x[0] == "rcpt":
                    rcpt_to(x, pipelin=True)
                elif x[0] == "data":
                    data(x, pipelin=True )
                else:
                    pass
            connver_data["Pipeline_mode"] = False
            
    try:
        send_header()
        print_log("Polaczenie z " + str(socket_adres[0]))
        while True:
            if connver_data["Close"] == True:
                print_log("Zakonczone polaczenie")
                socket_client.close()
                break
            if connver_data["Start_tls"] == True and connver_data["TLS_is"] == False:
                socket_client = ssl.wrap_socket(socket_client, server_side=True, certfile=config.ssl_cert_file, keyfile=config.ssl_key_file, ssl_version=ssl.PROTOCOL_SSLv23 , do_handshake_on_connect=False )
                connver_data["Start_tls"] = False
                connver_data["TLS_is"] = True
            msg = socket_client.recv(4096)
            if msg:
                if connver_data["Input"] == False:
                    check_commnad(parse_req(msg))
                else:
                    if msg[len(msg)-len(b"\r\n.\r\n"):] == b"\r\n.\r\n" or msg.replace(b"\r", b"").replace(b"\n", b"") == b".":
                        if len(connver_data["Data"]) <= config.max_size_of_mails:
                            connver_data["Data"] += msg
                            print_log("Odebrano widadomosc od {} ".format(connver_data["Mail"]))
                            send_response("250 OK\r\n")
                            connver_data["Input"] = False
                            scanner_mailer.start_mail(connver_data["Mail"], connver_data["Rcpt"], connver_data["Data"])
                        else:
                            send_response("552 message is too huge for this server\r\n")
                            connver_data["Input"] = False
                            connver_data["Data"] = ""
                    else:
                        connver_data["Data"] += msg 
    except Exception as e:
        databasa.make_smtp_log(str(e) + " (CON_ERROR)")

def smtp_start_connection():
    try:
        smtp = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
        smtp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        smtp.bind((config.smtp_host, config.smtp_port))
        smtp.listen(200)
        
        while True:
            client_socket, addres_socket = smtp.accept()
            if databasa.check_if_baned(addres_socket[0]) == False:
                threading.Thread(target=conversation, args=(client_socket, addres_socket,)).start()
            else:
                client_socket.send("421 Your addres is [{}] is temporary blocked\r\n".format(addres_socket[0]).encode() )
                client_socket.close()
    except Exception as e:
        databasa.make_smtp_log(str(e) + "  (STAR_ERROR)")

smtp_start_connection()
