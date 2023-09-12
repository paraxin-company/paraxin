import os

def change_name(file_name):
    # TODO: change file name
    return str(file_name).replace(' ', '_') if ' ' in file_name else file_name


def is_valid(file_name):
    # TODO: check file format
    valid_format = ['.jpg', '.png', '.jfif']
    return os.path.splitext(file_name)[1] in valid_format


def get_url(path, folder):
    # TODO: get url for save in database
    new_file_name = change_name(os.path.basename(path))

    dir = os.path.join('media', folder)
    new_path = os.path.join(dir, new_file_name)

    return new_path.replace('\\', '/')


def delete_file(file_address):
    try:
        base_url = 'paxi/static'
        complate_file_address = os.path.join(base_url, file_address)

        os.remove(complate_file_address)
        
        return True
    except:
        return False