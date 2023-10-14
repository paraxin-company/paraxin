def show(data): #TODO: return comma with enter (for show data)
    return data.replace(',', '\n')


def save(data): #TODO: return enter with comma (for save data)
    data_list = data.split('\r\n')
    result = []
    for key in data_list:
        if len(key) != 0 and len(key) > 0:
            result.append(key)
    
    return ','.join(result)