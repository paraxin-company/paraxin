from hashlib import sha256, md5

def get_hash(phrase):
    #TODO: hash phrase and return hashed text
    return sha256(phrase.encode()).hexdigest()


def check_pass(hashed, phrase):
    #TODO: check hashed phrase to other phrase
    if hashed == get_hash(phrase):
        return True
    return False

def small(name):
    return md5(name.encode()).hexdigest()[:20]