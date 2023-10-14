from paxi import folder_upload
import os

def check_name(name):
    # check folder name
    not_valid_list = ['\\','/','?','"','|','*','<','>',':']

    for item in not_valid_list:
        if item in name:
            return f'کاراکتر وارد شد مورد قبول نیست ({item})'
    return True 


def create(folder_name ,name):
    #TODO: create folder in path with name
    try:
        path = os.path.join(folder_upload, folder_name)

        os.mkdir(os.path.join(path,name))
        return True
    except:
        return False


def rename(folder_name, old_name, new_name):
    #TODO: rename folder in path with new name
    try:
        old_path = os.path.join(folder_upload, os.path.join(folder_name, old_name))
        new_path = os.path.join(folder_upload, os.path.join(folder_name, new_name))
        
        os.rename(old_path, new_path)
        return True
    except:
        return False