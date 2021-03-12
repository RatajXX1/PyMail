import base64
import databasa

metody_logowania = ["AUTH PLAIN LOGIN"]

def auth_set(cmd, sock, addres, data_buffer):
    if cmd[1:]:
        if data_buffer["Logged"] == False:
            if cmd[1].lower() == "plain":
                auth_plain(sock, addres, data_buffer, cmd)
            elif cmd[1].lower() == "login":
                auth_login(sock, addres, data_buffer)
            else:
                sock.send(b"500 not supported methods\r\n")
        else:
            sock.send("500 you already logged in <{}>\r\n".format(data_buffer["Use_mail"]).encode() )
    else:
        sock.send(b"500 not methods\r\n")

def auth_plain(sock, addres, data_buffer, cmds):
    
    def parse_resp(resp_send):
        for x in ["\r", "\n"]:
            resp_send.replace(x, "")
        return resp_send

    def login(mseg):
        try:
            odkodowane = base64.b64decode(mseg)
            if type(odkodowane) == bytes:
                odkodowane = odkodowane.decode()
            odkodowane = odkodowane.replace("\\@", "\x00")
            w = parse_resp(odkodowane).split("\x00")
            w = [x for x in w if x]
            if len(w) == 3:
                del w[1]
            elif len(w) > 2:
                return False

            logined = w[0]
            password = w[1]
            for x in ["'", '"']:
                logined = logined.replace(x, "")
                password = password.replace(x, "")

            succes = databasa.login_check(logined, password)
            return succes
        except Exception as e:
            return False
    msg = b""
    if type(cmds) == list and cmds[2:]:
        msg = cmds[2]
    else:
        sock.send(b"334 OK go\r\n")
        msg = sock.recv(4096)
    if msg or msg != b"":
        chekc = login(msg)
        if chekc != False:
            databasa.make_auth_logs(addres[0], " Success login into {} (AUTH PLAIN)".format(chekc))
            sock.send("250 OK succesfull login to <{}>\r\n".format(chekc).encode())
            data_buffer["Logged"] = True
            data_buffer["Use_mail"] = chekc
        else:
            sock.send(b"500 wrong password or login \r\n")
    else:
        sock.send(b"500 NO Responose")

def auth_login(sock, addres, data_buffer):
    def parse_resp(resp_send):
        for x in ["\r", "\n"]:
            resp_send.replace(x, "")
        return resp_send
    
    def login(logins, passsword):
        try:
            if type(logins) == bytes and type(passsword) == bytes:
                logins = base64.b64decode(logins).decode()
                passsword = base64.b64decode(passsword).decode()
                un_login = parse_resp(logins)
                un_password = parse_resp(passsword)
                return databasa.login_check(un_login, un_password)
            return False
        except:
            return False

    logined = "unknow"
    Haslo = "unknow"
    sock.send(b"334 " + base64.b64encode(b"Username") + b" \r\n")
    msg = sock.recv(4096)
    if msg:
        logined = msg
        sock.send(b"334 " + base64.b64encode(b"Password") + b" \r\n")
        msg = sock.recv(4096)
        if msg:
            Haslo = msg
            chekc = login(logined, Haslo)
            if chekc != False:
                databasa.make_auth_logs(addres[0], " Success login into {} (AUTH LOGIN)".format(chekc) )
                sock.send("235 OK succesfull login to <{}> \r\n".format(chekc).encode())
                data_buffer["Logged"] = True
                data_buffer["Use_mail"] = chekc
            else:
                sock.send(b"500 login or password is wrong \r\n")
        else:
            sock.send(b"500 No responose\r\n")
    else:
        sock.send(b"500 No responose\r\n")







