import config
import threading
from email.parser import Parser 
import databasa
import os
import smtp_connect

#
# TODO: SPAM filter
#

def save_mail(from_mail, to_mail, data, sended):
    def save_as_file(to ,data_mail):
        dirname = os.path.dirname(__file__)
        if os.path.isdir(os.path.join(dirname, "mailbox")) == False:
            os.mkdir(os.path.join(dirname, "mailbox"))
        
        if os.path.isdir(os.path.join(dirname, "mailbox/" + to_mail)) == False:
            os.mkdir(os.path.join(dirname, "mailbox/" + to_mail))
        
        ids = databasa.get_count_mails(to_mail)
        file_name = str(ids+1) + ".txt"
        if os.path.isfile(os.path.join(dirname, "mailbox/" + to_mail + "/" + file_name)) == True:
            while True:
                ids += 1
                file_name = str(ids) + ".txt"
                if os.path.isfile(os.path.join(dirname, "mailbox/" + to_mail + "/" + file_name)) == False:
                    break
        path = os.path.join(dirname, "mailbox/" + to_mail + "/" + file_name)

        file_txt = open(path, "w")
        if type(data_mail) == bytes:
            data_mail = data_mail.decode()
        file_txt.writelines(data_mail) 
        file_txt.close()
        return path
    if type(data) == bytes:
        data = data.decode()
    msg = Parser().parsestr(data)
    subject = ""
    if not msg["subject"]:
        subject = "Wiadomosc od " + from_mail
    else:
        subject = msg["Subject"]
    path = "XXXXXXXXXX"
    
    if sended == False:
        if type(to_mail) == list:
            for x in to_mail:
                path = save_as_file(x, data)
                databasa.index_order_mail(from_mail, x, subject, path)              
        else:
            path = save_as_file(to_mail, data)
            databasa.index_order_mail(from_mail, to_mail, subject, path)
    else:
        if type(from_mail) == list:
            for x in from_mail:
                path = save_as_file(x, data)
                databasa.index_sended_mail(to_mail, from_mail, subject, path)
        else:
            path = save_as_file(from_mail, data)
            databasa.index_sended_mail(to_mail, from_mail, subject, path)
        

def make_mime(data):
    pass

def start_mail(from_mail, to_mail, data):
    if from_mail.split("@")[1] in config.MX_domains:
        if type(to_mail) == list:
            mail_mx = []
            mail_normal = []
            for i,v in enumerate(to_mail):
                if v.split("@")[1] in config.MX_domains:
                    mail_mx.append(v)
                else:
                    mail_normal.append(v)
            if len(mail_mx) > 0:
                threading.Thread(target=save_mail, args=(from_mail, mail_mx, data, True )).start()
            if len(mail_normal) > 0:
                threading.Thread(target=save_mail, args=(from_mail, mail_normal, data, True, )).start()
                smtp_connect.add_coonection(from_mail, mail_normal, data)
        else:
            if to_mail.split("@")[1] in config.MX_domains:
                threading.Thread(target=save_mail, args=(from_mail, to_mail, data, True, )).start()
            else:
                threading.Thread(target=save_mail, args=(from_mail, to_mail, data, True, )).start()
                smtp_connect.add_coonection(from_mail, to_mail, data)
    else:
        threading.Thread(target=save_mail, args=(from_mail, to_mail, data, False)).start()







