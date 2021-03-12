create table Mail_authorize_logs
(
    from_ip   varchar(100)                       null,
    logs_text varchar(600)                       null,
    data_time datetime default CURRENT_TIMESTAMP null
);

create table Mail_inbox_mail
(
    ID_ac      int default 0 null,
    sent       int default 0 null,
    seen       int default 0 null,
    subject    varchar(1000) null,
    mail_box   varchar(500)  null,
    from_mail  varchar(500)  null,
    rcpt_mail  varchar(500)  null,
    index_path varchar(500)  null
);

create table Mail_send_logs
(
    from_mail  varchar(500)                       null,
    to_mail    varchar(500)                       null,
    domain_nam varchar(300)                       null,
    logs_text  varchar(600)                       null,
    data_time  datetime default CURRENT_TIMESTAMP null
);

create table Mail_smtp_server_logs
(
    logs_text varchar(600)                       null,
    data_time datetime default CURRENT_TIMESTAMP null
);

create table Mail_users
(
    IDS           int auto_increment
        primary key,
    Mail_Login    varchar(300)                       null,
    Mail_Password varchar(300)                       null,
    mail_name     varchar(500)                       null,
    createdAC     datetime default CURRENT_TIMESTAMP null
);

create table banned_IP
(
    IP_ADDRES   varchar(200)                       null,
    to_data     datetime                           null,
    when_banned datetime default CURRENT_TIMESTAMP null
);

