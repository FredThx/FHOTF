import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email import encoders
from pathlib import Path
import logging


class Smtp:
    ''' Un client smtp
    '''

    def __init__(self, host, port = 587, sender_address = None, sender_pass = None):
        '''Initialisation
        - host            :     hostname or IP
        - port            :     TCP-IP port
        - sender_address  :     ex : "toto@gmail.com"
        - sender_pass     :     password
        '''
        self.host = host
        self.port = port
        self.sender_address = sender_address
        self.sender_pass = sender_pass

    def send(self, receiver_address, subject = "", body = "", attach_file_name = None, sender_address = None, sender_pass = None ):
        ''' Send a message
        '''
        if sender_address is None:
            sender_address = self.sender_address
        if sender_pass is None:
            sender_pass = self.sender_pass
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
        #Create SMTP session for sending the mail
        session = smtplib.SMTP(self.host, self.port)
        session.starttls() #enable security
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        logging.debug("Email %s send!"%subject)

if __name__ == "__main__":
    smtp = Smtp('smtp.gmail.com', 587, 'fredthxdev@gmail.com', "555dcfg8***")
    smtp.send('fredthx@gmail.com', "Essai", "C'est juste un test","../hotfolder/888.txt")
