
# ----- GENERAL ------

Server_name = "smtp.example.com"

Hostname = "example.com"


#domains of emial rcpt ( root@example.com )
MX_domains = [
    "example.com"
]

# max sieze mails in bytes 
max_size_of_mails = 157286400 # 150 MB

ssl_cert_file = ""
ssl_key_file = ""


# ----- DATABASE -----

database_type = "MYSQL"

MYSQL_user = "root"
MYSQL_password = "password"
MYSQL_host = "localhost"
MYSQL_datbase = "database"

# ------- SMTP -------

smtp_host = "192.168.0.2" #"localhost"
smtp_port = 25
smtp_SSL = True
smtp_port_SSL = 143

SMTP_enable_TLS = True

#--------------------

