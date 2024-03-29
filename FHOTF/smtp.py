import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email import encoders
from pathlib import Path
import logging

import FHOTF.utils as utils

class Smtp:
    ''' Un client smtp
    '''

    def __init__(self, host, port = 587, sender_address = None, sender = None, sender_pass = None, starttls = True):
        '''Initialisation
        - host            :     hostname or IP
        - port            :     TCP-IP port
        - sender_address  :     ex : "toto@gmail.com"
        - sender_pass     :     password
        - sender          :     sender user (if != sender_address)
        - starttls        :     if True (default), use starttls before send email
        '''
        self.host = host
        self.port = port
        self.sender_address = sender_address
        self.sender = sender
        self.sender_pass = sender_pass
        self.starttls = starttls
        logging.debug(f"{self} created.")

    def __repr__(self):
        return f"Smpt({self.host}:{self.port}(user:{self.sender}/{self.sender_pass}, sender:{self.sender_address}))"


    def send(self, receiver_address, subject = "", body = "", attach_file_name = None, sender_address = None):
        ''' Send a message
        return True si ok
        '''
        if attach_file_name:
            dict_file = utils.dict_file(attach_file_name)
            subject  = subject.format(**dict_file)
            body = body.format(**dict_file)
        if sender_address is None:
            sender_address = self.sender_address or self.sender
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = subject
        #The body
        message.attach(MIMEText(body, 'plain'))
        # the attachment file
        if attach_file_name:
            attach_file_name = Path(attach_file_name)
            with open(str(attach_file_name), 'rb') as attach_file: # Open the file as binary mode
                payload=MIMEApplication(attach_file.read(), _subtype = attach_file_name.suffix)
            payload.add_header('Content-Disposition', 'attachment', filename=attach_file_name.name)
            message.attach(payload)
        text = message.as_string()
        #Create SMTP session for sending the mail
        try:
            logging.debug(f"Smtp session : {self}")
            session = smtplib.SMTP(self.host, self.port)
            session.ehlo()
            if self.starttls:
                session.starttls()
            if self.sender:
                try:
                    logging.debug(f"login{self.sender}")
                    session.login(self.sender, self.sender_pass)
                except:
                    pass
            session.sendmail(sender_address, receiver_address, text)
            logging.debug(f"Email ({subject}) send!")
            session.quit()
            return True
        except Exception as e:
            logging.error(f"Smtp error : {e}")



class NoneSmtp():
    '''A do-nothig Smtp class
    '''
    def __init__(self):
        logging.info("Create de do-nothing Smtp class")

    def send(self, *args, **kwargs):
        logging.info("No-send nothing.")


if __name__ == "__main__":
    smtp = Smtp('smtp.gmail.com', 587, 'fredthxdev@gmail.com', "555dcfg8***")
    smtp.send('fredthx@gmail.com', "Essai", "C'est juste un test","../hotfolder/888.txt")
