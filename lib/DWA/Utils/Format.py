def add_frame(str):
        lines = str.split('\n')
        res = '#' * 70
        res += '\n'
        for line in lines:
                res += '# %s\n' % (line,)

        res += '#' *  70
        res += '\n'
        return res

def humanize_time(seconds, format=False):
    (mins, secs) = divmod(seconds, 60)
    (hours, mins) = divmod(mins, 60)
    days = 0
    if hours > 24:
        (days, hours) = divmod(hours, 24)
    if format:
        str=''
        if days > 0:
            str = '%d days ' % days
        str = '%s%02d:%02d:%05.2f' % (str, hours, mins, secs)
        return str
    return (days, hours, mins, secs)
