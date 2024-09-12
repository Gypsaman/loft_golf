import ssl
import email
from email.message import EmailMessage
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json
import time
import os
from typing import List,Dict
import imaplib
from webproject.modules.dotenv_util import initialize_dotenv


servers = {
    "UB":  { "emailServer": "smtp.office365.com", "emailPort": 587, "emailAccount": "cegarcia@bridgeport.edu","password_source":"UBPassword"},
    "DNA": { "emailServer": "smtp.ionos.com", "emailPort": 587, "emailAccount": "cesar@distributedneuralapplications.com","password_source":"NeuroEmail"},
    "LOFT": {"emailServer": "smtp.privateemail.com", "emailPort": 587, "emailAccount":"loft@neurodna.xyz","password_source":"LOFTPassword"}
}
initialize_dotenv()

class Email:
    
    def __init__(self) -> None:
        server = os.environ.get('EMAIL_SERVER').strip()
        
        self.emailServer = servers[server]['emailServer'] #smtp.office365.com
        self.emailPort = servers[server]['emailPort'] #587

        self.password = os.environ.get(servers[server]['password_source']).strip()
        self.emailAccount = servers[server]['emailAccount']

        self.context = ssl.create_default_context()

        self.mailserver = smtplib.SMTP(self.emailServer,self.emailPort)
        self.mailserver.ehlo()
        self.mailserver.starttls()
        self.mailserver.login(self.emailAccount, self.password)

    def send_email(self,recipient,subject,body,carboncopy=None) -> None:
            
            em = EmailMessage()
            recipients = [recipient]
            if carboncopy is not None:
                recipients.append(carboncopy)
            
            em['From'] = self.emailAccount
            em['To'] = recipient
            if carboncopy is not None:
                em['Cc'] = carboncopy
            em['Subject'] = subject

            body = body

            em.set_content(body)
            self.mailserver.sendmail(self.emailAccount,recipients,em.as_string())
            
            
    def send_multipart_email(self,recipient,subject,body,html,carboncopy=None) -> None:
        msg = MIMEMultipart()
        msg['From'] = self.emailAccount
        msg['To'] = recipient
        if carboncopy is not None:
            msg['Cc'] = carboncopy
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        self.mailserver.send_message(msg)
        
    def bulk_email(self,emails: List[Dict[str,str]])-> None:
        
        for idx,email in enumerate(emails): 

            self.send_email(recipient=email['email'],subject=email['subject'],body=email['body'])
            
            if idx % 5:
                time.sleep(5)

    def receive_emails(self):
        imap = imaplib.IMAP4_SSL('mail.privateemail.com')

        try:
            imap.login('loft@neurodna.xyz','johnjordan')
        except imap.error as e:
            print(e)

        imap.select('inbox')
        status, messages = imap.search(None, 'UNSEEN')

        email_ids = messages[0].split()
        emails = []
        for email_id in email_ids:
            content = []
            res,msg = imap.fetch(email_id, '(RFC822)')
            for response in msg:
                if isinstance(response, tuple):
                    # Parse the email content
                    msg = email.message_from_bytes(response[1])
                    
                    # Decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # If it's a bytes object, decode to string
                        subject = subject.decode(encoding if encoding else "utf-8")
                    # Get the sender's email address
                    from_ = msg.get("From")

                    
                    # If the email message is multipart (i.e., contains text, HTML, attachments, etc.)
                    if msg.is_multipart():
                        for part in msg.walk():
                            # Extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            # Get the email body
                            try:
                                body = part.get_payload(decode=True).decode()
                                content.append(body)
                            except:
                                pass

                    else:
                        # If the email is not multipart
                        body = msg.get_payload(decode=True).decode()
                        content.append(body)

            emails.append({'subject':subject,'from':from_,'content':content})
        # Close the connection and logout
        imap.close()
        imap.logout()

        return emails
