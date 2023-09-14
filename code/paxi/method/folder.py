import os

base_url = r'paxi\static\media'

def check_name(name):
    not_valid_list = ['\\','/','?','"','|','*','<','>',':']

    for item in not_valid_list:
        if item in name:
            return f'کاراکتر وارد شد مورد قبول نیست ({item})'
    return True 


def create(folder_name ,name): #TODO: create folder in path with name
    try:
        global base_url
        path = os.path.join(base_url, folder_name)

        os.mkdir(os.path.join(path,name))
        return True
    except:
        return False


def rename(folder_name, old_name, new_name): #TODO: rename folder in path with new name
    try:
        global base_url
        old_path = os.path.join(base_url, os.path.join(folder_name, old_name))
        new_path = os.path.join(base_url, os.path.join(folder_name, new_name))
        
        os.rename(old_path, new_path)
        return True
    except:
        return False