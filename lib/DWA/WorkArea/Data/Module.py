# vim: sts=4 ts=8 et ai

#from Revision import Revision


class Module(object):
    def __init__(self, scm, directory, name, **kw):
        self.scm = scm
        self.directory = directory
        self.name = name
        self.saved_kw = dict(kw)
        self.name_only = kw.pop('name_only', False)
        self.tags = ''
        self.skip_tags = ''

        self.__dict__.update(kw)

    def get_definition(self):
        res = self.__class__.__name__ + "('%s', '%s'" % (self.directory, self.name)

        for key, value in self.saved_kw.items():
            res += ", " + key + "="
            if type(value) == type(''):
                res += "'" + value + "'"
            else:
                res += '{0}'.format(value)
        res += ')'
        return res

    def __str__(self):
        return "{}/{}".format(self.directory, self.name)

    def get_module_instance(self, branch, version, work_area):
        raise NotImplementedError
