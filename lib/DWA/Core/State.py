root_dir = '/tmp'

def get_dir(name):
    if len(name) and name[0] == '/':
        name = name[1:]
    return '{}/{}'.format(root_dir, name)
