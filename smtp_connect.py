import socket 
import threading
import queue
import dns.resolver
import config
import ssl
import databasa
q = queue.Queue()

def smtp_connect_to():
    
    def get_MX_domains(domain):
        try:
            resolves = dns.resolver.Resolver()
            query = resolves.resolve(domena, 'MX')
            domen = []
            for x in query:
                text = x.exchange.to_text()
                if text[len(text)-1] == ".":
                    text = list(text)
                    del text[len(text)-1]
                    text = "".join(text)
                domen.append([text, x.preference])

            def sorteds(tu):
                return tu[1]
            domen.sort(key=sorteds)
            return domen
        except:
            return False
    
    def show_alert(msg, date, host_name="" ):
        if type(msg) == bytes:
            msg = msg.decode()
        elif type(msg) != str:
            msg = str(msg)
        databasa.make_log_send(str(date[0]), str(date[1]), host_name, msg)       

    def check_smtp_server(msg):
        if type(msg) == bytes:
            msg = msg.decode()
        code = msg.split(" ")[0]
        resp_text = msg[len(code)+1:]
        if code == "220":
            return True
        else:
            return False
    
    def make_hello(sock):
        sock.send(b"ehlo " + config.Hostname.encode() + b"\r\n")
        msg = s.recv(4096)
        if msg:
            msg = msg.decode().replace("\r", "").split("\n")
            funkcje = []
            for i,x in enumerate(msg):
                if i > 0:
                    funkcje.append(x.replace("250", "" ).replace("-", "").lower())
            tabs = []
            for x in funkcje:
                if x != "":
                    if x[len(x) - 1] == " ":
                        x = list(x)
                        del x[len(x)-1]
                        x = "".join(x)
                    if x[0] == " ":
                        x = list(x)
                        del x[0]
                        x = "".join(x)
                    tabs.append(x)
            funkcje = tabs
            return funkcje
        else:
            return False
    
    def to_mail(sock, to):
        sock.send("rcpt to:<{}>\r\n".format(to).encode())
        msg = sock.recv(4096)
        if msg:
            code = msg.decode().split(" ")[0]
            if code == "250":
                return True
            else:
                return [False, msg.decode()]
        else:
            return False
    
    def from_mail(sock, to, functions, size=0):
        def arguments(in_fuctions):
            for x in in_fuctions:
                if 'size' == x.split(" ")[0]:
                    return True
            return False
        
        if arguments(functions) == True:
            sock.send("mail from:<{}> size={}\r\n".format(to, str(size)).encode())
        else:
            sock.send("mail from:<{}>\r\n".format(to).encode())

        msg = sock.recv(4096)
        if msg:
            code = msg.decode().split(" ")[0]
            if code == "250":
                return True
            else:
                return [False, msg.decode()]
        else:
            return False


    def send_data(sock, mesg, data_functions):
        sock.send(b"data\r\n")
        msg = s.recv(4096)
        if msg:
            code = msg.decode().split(" ")[0]
            if code == "354":
                if type(mesg) == bytes:
                    mesg = mesg.decode()
                if mesg[len(mesg) - len("\r\n.\r\n"):] != "\r\n.\r\n":
                    mesg += mesg + "\r\n.\r\n"
                if "smtputf8" in data_functions:
                    mesg = mesg.encode("utf-8")
                else:
                    mesg = mesg.encode()
                sock.send(mesg)
                msg = sock.recv(4096)
                if msg.decode().split(" ")[0] == "250":
                    return True
                else:
                    return [False, msg.decode()]
            else:
                return [False, msg.decode()]
        else:
            return False

    def connection_smtp(sock, msg, data_buffer, opt_items):
        if data_buffer["Check_smtp"] == False:
            check = check_smtp_server(msg)
            if check == True:
                data_buffer["Check_smtp"] = True
                func = make_hello(sock)
                if func != False:
                    data_buffer["hello"] = True
                    data_buffer["funtions"] = func
                    if "starttls" in func:
                        data_buffer["Use_tls"] = True
                else:
                    show_alert("Nie mozna zweryfikowac funckji Sewer SMTP (EHLO)", opt_items)
            else:
                show_alert("Serwer nie pozwala na rozpoczeczenie konwersacji (SMTP)", opt_items) 
        else:
            sended = from_mail(sock, msg[0], data_buffer["funtions"])
            if sended == True:
                sended = to_mail(sock, msg[1])
                if sended == True:
                    sended = send_data(sock, msg[2], data_buffer["funtions"])
                    if sended == True:
                        data_buffer["Succes"] = True
                        show_alert("Pomyslnie przeslanow wiadmosc", msg)
                    else:
                        if type(sended) == list:
                            show_alert(sended[1] + " (DATA)", msg)
                        else:
                            show_alert("Serwer nie odpowiada na komende DATA", msg)
                else:
                    if type(sended) == list:
                        show_alert(sended[1] + " (RCPT)", msg)
                    else:
                        show_alert("Serwer nie odpowiada na komende RCPT to", msg)
            else:
                if type(sended) == list:
                    show_alert(sended[1] + " (MAIL)", msg)
                else:
                    show_alert("Serwer nie odpowiada na komende Mail from", msg)
                

    while True:
        itmes = q.get()
        if type(itmes[1]) != list:
            domena = itmes[1].split("@")[1]
            if domena == "test.pl":
                domeny_MX = [["192.168.0.31", 5]]
            else:
                domeny_MX = get_MX_domains(domena)
            if domeny_MX != False:
                for index,x in enumerate(domeny_MX):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(5)
                        s.connect((x[0], 25))

                        show_alert("Udalo sie polaczyc ", itmes, host_name=x[0])
                        conn_buffer = {
                            "Check_smtp": False,
                            "Succes" : False,
                            "hello": False,
                            "from": False,
                            "to_mail": False,
                            "send_data": False,
                            "Use_tls": False,
                            "funtions": []
                        }

                    
                        msg = s.recv(4096)
                        if msg:
                            connection_smtp(s, msg, conn_buffer, itmes)
                            if conn_buffer["Use_tls"] == True:
                                s.send(b"starttls\r\n")
                                msg = s.recv(4096)
                                s = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
                            if conn_buffer["Check_smtp"] == True:
                                connection_smtp(s, itmes, conn_buffer, None)
                        else:
                            pass

                        if conn_buffer["Succes"] == True:
                            s.send(b"quit\r\n")
                            msg = s.recv(4096)
                            show_alert("Pomyslnie wyslanoe", itmes, host_name=x[0])
                            s.close()
                            break
                        else:
                            if index == (len(domeny_MX)-1):
                                show_alert("Nie udalo sie wylac wiadomosci (CON_ERROR)", itmes, host_name=x[0])
                            s.send(b"quit\r\n")
                            s.recv(4096)
                            s.close()
                    except Exception as e:
                        if index == (len(domeny_MX)-1):
                            show_alert("Nie udalo sie wysalc wiadomsci (HAR_ERROR)", times, host_name=x[0] )
                        show_alert(str(e) + " ( Nie udalo sie wylac )" , itmes, host_name=x[0])
            else:
                show_alert("Domena {} nie istnieje".format(domena), itmes)
        else:
            for i,v in enumerate(itmes[1]):
                domena = v.split("@")[1]
                domeny_MX = get_MX_domains(domena)
                if domeny_MX != False:
                    for index,x in enumerate(domeny_MX):
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(5)
                            s.connect((x[0], 25))

                            show_alert("Udalo sie polaczyc ", [itmes[0], v], host_name=x[0])
                            conn_buffer = {
                                "Check_smtp": False,
                                "Succes" : False,
                                "hello": False,
                                "from": False,
                                "to_mail": False,
                                "send_data": False,
                                "Use_tls": False,
                                "funtions": []
                            }

                            msg = s.recv(4096)
                            if msg:
                                connection_smtp(s, msg, conn_buffer, [itmes[0], v, itmes[2]] )
                                if conn_buffer["Use_tls"] == True:
                                    s.send(b"starttls\r\n")
                                    msg = s.recv(4096)
                                    s = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
                                if conn_buffer["Check_smtp"] == True:
                                    connection_smtp(s, [itmes[0], v, itmes[2]], conn_buffer, None)
                            else:
                                pass
                            if conn_buffer["Succes"] == True:
                                s.send(b"quit\r\n")
                                msg = s.recv(4096)
                                show_alert("Pomyslnie wyslano", [itmes[0], v], host_name=x[0])
                                s.close()
                                break
                            else:
                                if index == (len(domeny_MX)-1):
                                    show_alert("Nie udalo sie wyslac wiadomsci (CON_ERROR)", [itmes[0], v], host_name=x[0])
                                s.send(b"quit\r\n")
                                msg = s.recv(4096)
                                s.close()

                        except Exception as e:
                            if index == (len(domeny_MX)-1):
                                show_alert("Nie udalo sie wyslac wiadomsci (HAR_ERROR)", [itmes[0], v], host_name=x[0])
                            show_alert(str(e) + " ( Nie udalo sie wyslac )", [itmes[0], v], host_name=x[0])
                else:
                    show_alert("Nie znaleziono domeny {}".format(domena), [itmes[0], v])


        q.task_done()

        
threading.Thread(target=smtp_connect_to).start()

def add_coonection(from_mail, to_mail, data):
    global q
    q.put([from_mail, to_mail, data])
    q.join()
    
#add_coonection("ratajx1@gmail.com", ["admin@mdrproject.pl", "ratajx1@wp.pl"], "dsadsadsadasdasd")
    




