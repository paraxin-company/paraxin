import os, datetime

def change_name(file_name):
    # TODO: change file name
    renamed = str(file_name).replace(' ', '_') if ' ' in file_name else file_name
    return str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))+"1400."+renamed


def is_valid(file_name):
    # TODO: check file format
    valid_format = ['.jpg', '.png', '.jfif']
    return os.path.splitext(file_name)[1] in valid_format


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
    return filename.split('1400.')[1]