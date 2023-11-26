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