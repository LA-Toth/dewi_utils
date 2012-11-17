root_dir = '/tmp'


def get_dir(name):
    if len(name) and name[0] == '/':
        name = name[1:]
    return '{}/{}'.format(root_dir, name)


def set_root_dir(new_root_dir):
    global root_dir
    root_dir = new_root_dir


def get_root_dir():
    return root_dir
