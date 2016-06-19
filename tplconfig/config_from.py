# -*- coding: utf-8 -*-

import sys
import pprint
import os

import six
from six.moves.urllib.parse import urlparse

jsonmod = None

priority = ['simplejson', 'jsonlib2', 'json']
for mod in priority:
    try:
        jsonmod = __import__(mod)
    except ImportError:
        pass
    else:
        break

from six import StringIO

try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False
    
try:    
    import yaml
    from yaml import load as yaml_load    
    from yaml import dump as yaml_dump    
    HAVE_YAML = True
except ImportError as err:
    HAVE_YAML = False
else:
    try:
        from yaml import CLoader as YAMLLoader, CDumper as YAMLDumper
    except ImportError:
        from yaml import Loader as YAMLLoader, Dumper as YAMLDumper

from . import utils

def load_class(name):
    """Load class in module by name string

    Return class not instancied:
    >>> klass = load_class("email.parser.Parser")
    """
    
    if not name:
        return None

    if type(name) in six.class_types:
        return name
    
    if not "." in name: 
        raise ValueError("name %s is not class fullname or invalid package")
    
    name_split = name.split(".")
    
    module_name = ".".join(name_split[:-1])
    class_name = name_split[-1:][0]
    
    if not module_name in sys.modules:
        __import__(module_name)
        
    mod = sys.modules[module_name]

    return getattr(mod, class_name)
    

def load_module(module_name):
    """Load module by name string"""
    
    if not module_name:
        return None
    
    if ":" in module_name:
        module_name = module_name.replace(":", ".")
        return load_class(module_name)

    if not module_name in sys.modules:
        __import__(module_name)
        
    return sys.modules[module_name]
    

class Config(object):

    _BOOLEANS = {'1': True, 'yes': True, 'true': True, 'on': True,
                 '0': False, 'no': False, 'false': False, 'off': False}

    def __init__(self, config_from='env://', contenair={}, **settings):
        
        self._config_from = config_from or "env://"
        
        self._contenair = contenair or {}
        
        self._settings = settings
        
        self._loaded = False
        
    def get_items(self):
        if not self._loaded:
            self.load(self._config_from)
        return self._contenair
    items = property(fget=get_items)

    def _cast_boolean(self, value):
        """
        Helper to convert config values to boolean as ConfigParser do.
        """
        value = str(value)
        if value.lower() not in self._BOOLEANS:
            raise ValueError('Not a boolean: %s' % value)

        return self._BOOLEANS[value.lower()]

    def get(self, option, default=None, cast=None):
        """
        Return the value for option or default if defined.
        """
        if not self._loaded:
            self.load(self._config_from)
        
        if option in self._contenair:
            value = self._contenair.get(option)
        else:
            value = default

        if not cast:
            return value
        elif cast is bool:
            cast = self._cast_boolean

        return cast(value)

    def load(self, config_from=None, force_reload=False):
        """
        python://
        env://
        yaml://
        json://
        http://, https://
        """
        config_from = config_from or self._config_from
        if not '://' in config_from:
            raise ValueError("Bad uri")
        
        scheme, name = config_from.split('://')
        scheme = scheme.lower()

        config = None
        
        if scheme in ['http', 'https']:
            config = config_from_http(config_from, **self._settings)
        elif scheme == 'env':
            config = config_from_env(**self._settings)
        elif scheme == 'python':
            config = config_from_object(name, **self._settings)
        elif scheme == 'json':
            config = config_from_json(name, **self._settings)
        elif scheme == 'yaml':
            config = config_from_yaml(name, **self._settings)
            
        if not config or len(config) == 0:
            raise Exception("config is not loaded")

        self._contenair = config
        
        self._loaded = True

    def __call__(self, *args, **kwargs):
        if not self._loaded:
            self.load(self._config_from)

        return self.get(*args, **kwargs)


def replace_with(kwargs):

    values = {}
    
    for k, v in six.iteritems(kwargs):
        
        #TODO: if list, verifier chaque valeur de la liste ?
        
        if isinstance(v, dict):
            values[k] = replace_with(v)
        else:
            if isinstance(v, six.string_types):
                
                if v.startswith("ENV_"):
                    key_env = v[4:]
                    value_env = os.environ.get(key_env, None)
                    values[k] = value_env
                
                elif v.startswith("FUNC_"):
                    key_func = v[5:]
                    func = utils.MY_FUNCTIONS.get(key_func, None)
                    if func:
                        values[k] = func(key=k, **values)
                    else:
                        values[k] = v
            else:
                values[k] = v
    
    return values

        


def config_from_http(url=None, silent=False, BANNED_SETTINGS=[], upper_only=False, to_lower=False, debug=False, **kwargs):
    """
    Usage:
    >>> config = config_from_http(url='http://httpbin.org/headers', upper_only=False)
    >>> 'headers' in config
    True
    >>> 'Host' in config.get('headers')
    True
    """

    if not url:
        if silent is False:
            raise ValueError(u"url parameter is required")
        else:
            return

    config = {}
    dict_update = {}

    try:    
        config = requests.get(url).json()
    except:
        if silent is False:
            raise

    try:
        for k, v in six.iteritems(config):
            
            if upper_only and not k.isupper():
                continue
            
            if not k in BANNED_SETTINGS:
                dict_update[k] = v                

    except:
        if silent is False:
            raise

    """
    if to_lower:
        #TODO: Tous transformer ? (sous dict)
        config = {}
        for k, v in dict_update.iteritems():
            config[k.lower()] = v
        
        return config
    """
    
    return dict_update

def config_from_json(filepath=None, fileobj=None, json_loader=None, silent=False, BANNED_SETTINGS=[], upper_only=False, debug=False, **kwargs):
    """
    Usage:
    >>> from StringIO import StringIO
    >>> fileobj = StringIO('{"DEBUG": true}')
    >>> config = config_from_json(fileobj=fileobj)
    >>> config.get('DEBUG')
    True
    """
    
    if not filepath and not fileobj:
        if silent is False:
            raise ValueError(u"Not filepath or fileobj in parameters")
        else:
            return

    if not json_loader:
        json_loader = jsonmod.load #per file object
            
    config = {}
    dict_update = {}

    try:    
        if not fileobj:
            with open(filepath, 'r') as fp:
                config = json_loader(fp)
        else:
            config = json_loader(fileobj)
    except:
        if silent is False:
            raise

    try:
        for k, v in six.iteritems(config):
            
            if upper_only and not k.isupper():
                continue
            
            if not k in BANNED_SETTINGS:
                dict_update[k] = v                

    except:
        if silent is False:
            raise
    
    return dict_update

def config_from_yaml(filepath=None, fileobj=None, silent=False, BANNED_SETTINGS=[], upper_only=False, parse_env=False, debug=False, **kwargs):
    """
    Usage:
    >>> from StringIO import StringIO
    >>> fileobj = StringIO('DEBUG: true')
    >>> config = config_from_yaml(fileobj=fileobj)
    >>> config.get('DEBUG')
    True
    
    #>>> os.getenv('TEST_HOSTNAME') == 'MYTEST'
    #True
    #>>> fileobj = StringIO('HOSTNAME: ENV_TEST_HOSTNAME')
    #>>> config = config_from_yaml(fileobj=fileobj, parse_env=True)
    #>>> config.get('HOSTNAME')
    #'MYTEST'
    """

    if not filepath and not fileobj:
        if silent is False:
            raise ValueError(u"Not filepath or fileobj in parameters")
        else:
            return {}
    
    if filepath and not os.path.exists(filepath):
        if silent is False:
            raise ValueError("file not found : %s" % filepath)
        else:
            return {}

    config = {}
    dict_update = {}

    try:    
        if not fileobj:
            with open(filepath, 'r') as fp:
                config = yaml_load(fp, Loader=YAMLLoader)
        else:
            config = yaml_load(fileobj, Loader=YAMLLoader)
    except:
        if silent is False:
            raise

    try:
        for k, v in six.iteritems(config):
            
            if upper_only and not k.isupper():
                continue
            
            if not k in BANNED_SETTINGS:
                dict_update[k] = v                

    except:
        if silent is False:
            raise

    if parse_env:
        dict_update = replace_with(dict_update.copy())        
        
    return dict_update

def config_from_env(start_name=None, environ=None, debug=False, **kwargs):
    
    dict_update = {}
    
    for key in os.environ.keys():
        if not start_name:
            dict_update[key] = os.environ.get(key)        
        elif key.startswith(start_name):
            dict_update[key] = os.environ.get(key)
    
    return dict_update

def config_from_object(obj=None, silent=False, BANNED_SETTINGS=[], upper_only=True, debug=False, **kwargs):
    u"""Importe les variables d'un module ou d'une classe dans un module
    
    Exclu le remplacement des variables situés dans BANNED_SETTINGS

    >>> class Test(object):
    ...    VAR1 = "test"
    ...
    >>> config = config_from_object(Test)
    >>> config.has_key('VAR1')
    True
        
    >>> config = config_from_object("tplconfig.tests.resources.dummy:Test1")
    >>> config.has_key('VAR1')
    True
    
    >>> config = config_from_object("tplconfig.tests.dummy", upper_only=False)
    >>> config.has_key('Test1')
    True
    
    """
    BANNED_SETTINGS = BANNED_SETTINGS or []
    
    if obj is None:
        raise ValueError("obj is required")

    dict_update = {}
    
    try:
        base_settings = obj
        
        if isinstance(obj, six.string_types):
            base_settings = load_module(obj)
        
        for k in dir(base_settings):
            
            if k.startswith("_"):
                continue
            
            if upper_only and not k.isupper():
                continue
            
            if not k in BANNED_SETTINGS:
                dict_update[k] = getattr(base_settings, k)                

    except:
        if silent is False:
            raise
    
    return dict_update

def export_config(config=None, export_path=None, format='stdout'):
    
    if format == 'stdout':
        pprint.pprint(config)
        return

    fp = None
    stdout = False    
    try:
        if export_path and export_path != 'stdout':
            fp = open(export_path, 'wt')
        else:
            stdout = True
            fp = StringIO()
    
        if format == 'yaml':
            yaml_dump(config, fp, Dumper=YAMLDumper, explicit_start=False, default_flow_style=False)
        
        elif format == 'json':
            jsonmod.dump(config, fp, indent=3)
    except:
        raise
    finally:
        if fp:
            if stdout:
                print(fp.getvalue())
            
            fp.close()


DEFAULT_CONFIG_LOADERS = {
    'python': config_from_object,
    'json': config_from_json,
}

if HAVE_YAML:
    DEFAULT_CONFIG_LOADERS['yaml'] = config_from_yaml

if HAVE_REQUESTS:
    DEFAULT_CONFIG_LOADERS['http'] = config_from_http
    
DEFAULT_CONFIG_EXPORTERS = ['json']#, 'stdout']

if HAVE_YAML:
    DEFAULT_CONFIG_EXPORTERS.append('yaml')
    
def _test():
    import doctest
    doctest.testmod()
    
if __name__ == "__main__":
    #Usage: python config_from.py --test
    """
    nosetests -s -v --with-doctest tplconfig
    
    Linux:
    TEST_HOSTNAME=MYTEST -m tplconfig.config_from --test
    Win:
    set TEST_HOSTNAME=MYTEST
    python -m tplconfig.config_from --test
    """
    import sys
    import logging
    if '-v' in sys.argv: logging.basicConfig(level=logging.DEBUG)
    if '--test' in sys.argv: _test() 
        