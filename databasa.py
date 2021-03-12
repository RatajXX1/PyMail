import mysql.connector
import config

def make_con():
    baza_sql = mysql.connector.connect(
        host = config.MYSQL_host,
        user = config.MYSQL_user,
        password = config.MYSQL_password,
        database = config.MYSQL_datbase
    )
    sql_cursor = baza_sql.cursor()
    return baza_sql, sql_cursor


def check_mail_exitst(mail):
    """

        Give: mail ( admin@mdrporject.pl )
        Return: true or false 

    """
    baza, cursor = make_con()

    cursor.execute("SELECT * FROM Mail_users WHERE mail_name = '{}' ;".format(mail))
    
    wyniki = cursor.fetchall()
    baza.close()
    if len(wyniki) > 0:
        return True
    else:
        return False 

def index_order_mail(from_mail, to_mail, subject, path):
    baza, cursor = make_con()
    
    cursor.execute("SELECT * FROM Mail_inbox_mail WHERE mail_box = '{}' ;".format(to_mail))
    
    ids = cursor.fetchall()
    if ids != None and len(ids) > 0:
        ids = len(ids) + 1
    else:
        ids = 0

    cursor.execute("INSERT INTO Mail_inbox_mail (ID_AC, subject, mail_box, from_mail, rcpt_mail, index_path) VALUES ({}, '{}', '{}', '{}', '{}', '{}' ) ;".format(str(ids), subject, to_mail, from_mail, to_mail, path))
    baza.commit()

    baza.close()

def index_sended_mail(from_mail, to_mail, subject, path):
    baza, cursor = make_con()
    
    cursor.execute("SELECT * FROM Mail_inbox_mail WHERE mail_box = '{}' ;".format(to_mail))
    ids = cursor.fetchall()
    if ids != None and len(ids) > 0:
        ids = len(ids) + 1
    else:
        ids = 0

    cursor.execute("INSERT INTO Mail_inbox_mail (ID_AC, sent, subject, mail_box, from_mail, rcpt_mail, index_path) VALUES ({}, 1, '{}', '{}', '{}', '{}', '{}' ) ;".format(str(ids), subject, to_mail, from_mail, to_mail, path ))
    baza.commit()
    baza.close()

def get_all_mails():
    baza, cursor = make_con()
    
    cursor.execute("SELECT mail_name FROM Mail_users;")
    
    wyniki = cursor.fetchall()

    baza.close()
    
    return wyniki


def get_count_mails(mailbox):
    baza, cursor = make_con()
    
    cursor.execute("SELECT * FROM Mail_inbox_mail WHERE mail_box = '{}';".format(mailbox))
    
    wyniki = len(cursor.fetchall())

    baza.close()
    
    return wyniki
    

def make_log_send(from_mails, to_mail, domain_name, text):
    baza, cursor = make_con()

    cursor.execute("INSERT INTO Mail_send_logs (from_mail, to_mail, domain_nam, logs_text ) VALUES ('{}', '{}', '{}' , '{}');".format(from_mails, to_mail, domain_name, text))

    baza.commit()
    baza.close()


def check_if_baned(addres_ip):
    from datetime import datetime
    baza, cursor = make_con()    
    cursor.execute("DELETE FROM banned_IP WHERE to_data < '{}';".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    baza.commit()
    cursor.execute("SELECT * FROM banned_IP WHERE IP_ADDRES = '{}';".format(addres_ip))
    wyniki = cursor.fetchall()
    baza.close()
    if len(wyniki) > 0:
        return True
    else:
        return False

def set_banned_ip(addres_ip):
    from datetime import datetime, timedelta
    baza, cursor = make_con()
    czas = datetime.now() + timedelta(hours=1)
    cursor.execute("INSERT INTO banned_IP (IP_ADDRES, to_data) VALUES ('{}', '{}');".format(addres_ip, czas.strftime("%Y-%m-%d %H:%M:%S")))
    baza.commit()
    baza.close()

def login_check(login, password):
    baza, cursor = make_con()
    cursor.execute("SELECT mail_name FROM Mail_users WHERE Mail_Login = '{}' and Mail_Password = '{}' ;".format(login, password))
    wyniki = cursor.fetchone()
    baza.close()
    if wyniki != None and len(wyniki) == 1:
        return wyniki[0]
    else:
        return False


def make_smtp_log(text):
    baza, cursor = make_con()
    cursor.execute("INSERT INTO Mail_smtp_server_logs (logs_text) VALUES ('{}') ;".format(text))
    baza.commit()
    baza.close()


def make_auth_logs(ip, text):
    baza, cursor = make_con()
    cursor.execute("INSERT INTO Mail_authorize_logs (from_ip, logs_text) VALUES ('{}', '{}') ;".format(ip, text))
    baza.commit()
    baza.close()






