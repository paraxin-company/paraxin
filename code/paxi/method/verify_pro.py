from paxi.panel.model import Verify
from paxi import db
from datetime import datetime

def check_not_expire(tocken_time):
    # check time is expire or no and then feedback
    time_now = datetime.now()

    if tocken_time.today() == time_now.today():
        tocken_time_splited = str(tocken_time.time()).split(':')
        time_now_splited = str(time_now.time()).split(':')

        if tocken_time_splited[0] == time_now_splited[0] and int(time_now_splited[1])-int(tocken_time_splited[1]) <= 3:
            return True
    return False


def get_tocken():
    #TODO: return random number
    from random import randrange

    return randrange(10000, 99999)


def email(value):
    #TODO: send tocken and save in database
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import smtplib

        tocken = get_tocken()
        
        msg = MIMEMultipart()
        msg['To'] = value
        msg['From'] = 'support@paraxin.ir'
        msg['Subject'] = 'تایید حساب ایمیل شما در پاراکسین'

        message = f"کد تایید شما در پاراکسین\n\ncode : {tocken}"
        msg.attach( MIMEText(message, 'plain') )

        with smtplib.SMTP('mail.paraxin.ir:25') as server:
            server.starttls()
            server.login(msg['From'], 'Aspad@1380')
            server.sendmail(msg['From'], msg['To'], msg.as_string())

        # save tocken in database
        db.session.add(Verify(tocken=tocken, item=value))
        db.session.commit()

        return True
    except:
        return f'برای ارسال کد به {value} مشکلی پیش آمده است'


def phone(value):
    #TODO: send tocken and save in database
    try:
        import kavenegar
        
        # get tocken for verify
        tocken = get_tocken()

        api = kavenegar.KavenegarAPI('Your API Key')
        params = {
            'sender': '1000xxxx',
            'receptor' : value,
            'message' : f"کد تایید شماره شما در پاراکسین\ncode:{tocken}"
        }   
        response = api.sms_send(params)

        if response == True:
            # save tocken in database
            db.session.add(Verify(tocken=tocken, item=value))
            db.session.commit()

            return True
        else:
            return 'پروسه ارسال پیامک حاوی کد تایید با اختلال مواجح شده است'
    except:
        return f'برای ارسال کد به {value} مشکلی پیش آمده است'