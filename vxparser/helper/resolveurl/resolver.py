#    ResolveURL XBMC Addon
#    Copyright (C) 2011, 2016 t0mm0, tknorris
#    OVERALL CREDIT TO:
#    t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import abc
from resolveurl import common
import six

abstractstaticmethod = abc.abstractmethod


class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class ResolverError(Exception):
    pass


class ResolveUrl(object):
    __metaclass__ = abc.ABCMeta

    name = 'generic'
    domains = ['localdomain']
    pattern = None
    net = common.Net()

    @abc.abstractmethod
    def get_media_url(self, host, media_id):
        raise NotImplementedError

    @abc.abstractmethod
    def get_url(self, host, media_id):
        raise NotImplementedError

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url, re.I)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        if isinstance(host, six.string_types):
            host = host.lower()

        if url:
            return re.search(self.pattern, url, re.I) is not None
        else:
            return any(host in domain.lower() for domain in self.domains)

    @classmethod
    def isUniversal(cls):
        return False

    @classmethod
    def isPopup(cls):
        return False

    def login(self):
        return True

    @classmethod
    def get_settings_xml(cls, include_login=True):
        xml = [
            '<setting id="%s_priority" type="number" label="%s" default="100"/>' % (cls.__name__, common.i18n('priority')),
            '<setting id="%s_enabled" ''type="bool" label="%s" default="true"/>' % (cls.__name__, common.i18n('enabled'))
        ]
        if include_login:
            xml.append('<setting id="%s_login" ''type="bool" label="%s" default="true" visible="false"/>' % (cls.__name__, common.i18n('login')))
        return xml

    @classmethod
    def set_setting(cls, key, value):
        common.set_setting('%s_%s' % (cls.__name__, key), str(value))

    @classmethod
    def get_setting(cls, key):
        return common.get_setting('%s_%s' % (cls.__name__, key))

    @classmethod
    def _get_priority(cls):
        try:
            return int(cls.get_setting('priority'))
        except:
            return 100

    @classmethod
    def _is_enabled(cls):
        # default behaviour is enabled is True if resolver is enabled, or has login set to "true", or doesn't have the setting
        return cls.get_setting('enabled') == 'true' and cls.get_setting('login') in ['', 'true']

    def _get_host(self, host):
        if '.' not in host:
            for domain in self.domains:
                if host in domain:
                    return domain

        return host

    def _default_get_url(self, host, media_id, template=None):
        if template is None:
            template = 'http://{host}/embed-{media_id}.html'
        host = self._get_host(host)
        return template.format(host=host, media_id=media_id)

    @common.cache.cache_method(cache_limit=1)
    def _auto_update(self, py_source, py_path, key=''):
        try:
            if self.get_setting('auto_update') == 'true' and py_source:
                headers = self.net.http_HEAD(py_source).get_headers(as_dict=True)
                common.logger.log(headers)
                old_etag = self.get_setting('etag')
                new_etag = headers.get('Etag', '')
                old_len = common.file_length(py_path, key)
                new_len = int(headers.get('Content-Length', 0))
                py_name = os.path.basename(py_path)

                if old_etag != new_etag or old_len != new_len:
                    common.logger.log('Updating %s: |%s|%s|%s|%s|' % (py_name, old_etag, new_etag, old_len, new_len))
                    self.set_setting('etag', new_etag)
                    new_py = self.net.http_GET(py_source).content
                    if new_py:
                        if key:
                            new_py = common.decrypt_py(new_py, key)

                        if new_py and 'import' in new_py:
                            with open(py_path, 'w') as f:
                                f.write(new_py.encode('utf-8'))
                            common.kodi.notify('%s %s' % (self.name, common.i18n('resolver_updated')))
                else:
                    common.logger.log('Reusing existing %s: |%s|%s|%s|%s|' % (py_name, old_etag, new_etag, old_len, new_len))
                common.log_file_hash(py_path)
        except Exception as e:
            common.logger.log_warning('Exception during %s Auto-Update code retrieve: %s' % (self.name, e))
