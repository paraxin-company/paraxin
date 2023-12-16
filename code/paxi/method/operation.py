import os


def copy_to_new_category(address,last_category, new_category):
    # TODO: this fuction can copy file from address to the new address and return new address as result
    image_address = address.replace(last_category, new_category)
    old_file = os.path.join('paxi', 'static', address)
    new_file = os.path.join('paxi', 'static', image_address)
    
    # copy old_file to the new address
    with open(str(old_file), mode='rb') as data:
        with open(str(new_file), mode='wb') as new_file_data:
            new_file_data.write(data.read())

    return image_address


class Send():
    #TODO: send 
    def __init__(self, destination, message, title) -> None:
        self.destination = destination
        self.message = message
        self.title = title
        self.response = False

    def as_email(self):
        try:
            #TODO: start sendding as email message
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import smtplib

            msg = MIMEMultipart()
            msg['To'] = self.destination
            msg['From'] = 'support@paraxin.ir'
            msg['Subject'] = self.title

            msg.attach( MIMEText(self.message, 'plain') )

            with smtplib.SMTP('mail.paraxin.ir:25') as server:
                server.starttls()
                server.login(msg['From'], 'Aspad@1380')
                server.sendmail(msg['From'], msg['To'], msg.as_string())

            self.response = True
        except:
            return self.response