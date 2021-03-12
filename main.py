import threading
import databasa
import os


def check_folders():
    dirname = os.path.dirname(__file__)
    if os.path.isdir(os.path.join(dirname, "mailbox")) == False:
        os.mkdir(os.path.join(dirname, "mailbox"))
    maile = databasa.get_all_mails()
    for x in maile:
        if os.path.isdir(os.path.join(dirname, "mailbox/" + x[0])) == False:
            os.mkdir(os.path.join(dirname, "mailbox/" + x[0]))

def main():
    check_folders()


main()


