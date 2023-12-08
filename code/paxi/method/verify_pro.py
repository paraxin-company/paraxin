from paxi.model import Verify
from paxi import db

def get_tocken():
    #TODO: return random number

    from random import randrange
    return randrange(10000, 99999)


def email(value):
    #TODO: send tocken and save in database
    try:
        tocken = get_tocken()

        # save tocken in database
        db.session.add(Verify(tocken=tocken, item=value))
        db.session.commit()

        return True
    except:
        return f'برای ارسال کد به {value} مشکلی پیش آمده است'


def phone(value):
    #TODO: send tocken and save in database
    try:
        tocken = get_tocken()

        # save tocken in database
        db.session.add(Verify(tocken=tocken, item=value))
        db.session.commit()

        return True
    except:
        return f'برای ارسال کد به {value} مشکلی پیش آمده است'