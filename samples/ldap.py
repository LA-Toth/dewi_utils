import typing

from ldap3 import Server, Connection


class LDAP:
    def __init__(self):
        self._conn = Connection(Server('ldap://foo.bar'), auto_bind=True)

    def search_by_email(self, email: str):
        result = self._search(f'(&(objectclass=person)(mail={email}))', ['uid', 'googleFamilyName', 'googleGivenName'])
        if result:
            return result[0]

    def _search(self, query: str, attributes: typing.List[str]):
        self._conn.search('dc=balabit', query, attributes=attributes)
        return self._conn.entries
