import os, datetime
from paxi.method import passwords

def rename_name(file_name):
    # TODO: change file name
    file_name = passwords.small(file_name)+os.path.splitext(file_name)[1]
    return str(datetime.datetime.now().strftime("%m-%d-%H-%M"))+"00."+file_name


def is_valid(file_name):
    # TODO: check file format
    valid_format = ['.jpg', '.ico', '.jpeg', '.icon', '.svg', '.webp', '.png', '.jfif']
    return os.path.splitext(file_name)[1] in valid_format


def is_valid_album(album):
    # TODO: check each image in album and them return realated value
    for item in album:
        if is_valid(item.filename) == False:
            return False
    return True


def get_url(path, folder):
    # TODO: return image url for save in database
    dir = os.path.join('media', folder)
    new_path = os.path.join(dir, os.path.basename(path))

    return new_path.replace('\\', '/')


def delete_file(file_address):
    # TODO: delete file in address and return state for delete image file
    try:
        base_url = 'paxi/static'
        complate_file_address = os.path.join(base_url, file_address)

        os.remove(complate_file_address)
        
        return True
    except:
        return False
    

def rename_undo(filename):
    # return filename
    return filename.split('00.')[1]