# vim: ts=8 sts=4 sw=4 et ai si

from DWA.WorkArea.Exceptions import WorkAreaError


NAME_ONLY_VERSION = '(name-only)'

products = {}


class Product(object):
    def __init__(self, name, versions, modules, **kw):
        global products
        self.aliases=kw.pop('aliases', list())
        if type(self.aliases) != list:
            self.aliases = [ self.aliases ]

        self.name_only = kw.pop('name_only', False)
        if self.name_only:
            products[(name, NAME_ONLY_VERSION)] = self
        else:
            for v in versions:
                products[(name, v)] = self
                for s in self.aliases:
                    products[(s, v)] = self

        self.name = name
        self.modules = modules
        self.versions = versions
        self.profile = kw.pop('profile', None)
        self.depends = kw.pop('depends', None)
        self.depends_exclude = kw.pop('depends_exclude', None)
        for k in kw:
            if k[:8] == 'modules_':
                key = k[8:]
                for m in self.modules:
                    setattr(m, key, kw[k])


    def get_module_list(self):
        names = []
        for m in self.modules:
            names.append(m.name)
        return names


    def get_module(self, name):
        for module in self.modules:
            if module.name == name:
                return module
        raise WorkAreaError('No such module {}/{}',format(self.name, name))


    def get_profile(self, branch, version):
        if self.profile:
            if '%' in self.profile:
                return self.profile % { 'branch': branch, 'version' : version }
            else:
                return self.profile.format(branch=branch, version=version)
        else:
            return None


    def __str__(self):
        if self.name_only:
            version_str = ' name-only=True'
        else:
            version_str = ' versions=' + str(self.versions)
        return 'Product: name=' + self.name + version_str + ' modules=' + str(self.get_module_list())



def get_product(name, version):
    import ProductList
    try:
        return products[(name, version)]
    except KeyError:
        while len(version) > 0:
            dot_pos = version.rfind('.')
            if dot_pos > 0:
                version = version[:dot_pos]
            else:
                break;
            if (name, version) in products:
                return products[(name, version)]
        try:
            return products[(name, '*')]
        except KeyError:
            raise WorkAreaError('No such product %s' % name)
