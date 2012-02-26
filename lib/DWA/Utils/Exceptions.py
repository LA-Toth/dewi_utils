# vim: sts=4 ts=8 et ai

from DWA.Utils.Screen import add_frame

def format_exception(with_traceback=False):
    einfo = sys.exc_info()
    tb_str = 'An exception occured:\n  Type: %s\n  Message: %s\n\n' % \
             (einfo[0].__name__, einfo[1])


    tb = traceback.extract_tb(einfo[2])
    for t in tb:
        tb_str += '  File %s:%s in %s\n    %s\n' % t

    tb_str = add_frame(tb_str)

    return tb_str
