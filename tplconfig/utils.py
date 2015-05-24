# -*- coding: utf-8 -*-

import os
import socket

_BOOLEANS = {'1': True, 'yes': True, 'true': True, 'on': True,
             '0': False, 'no': False, 'false': False, 'off': False}

def to_list(value):
    if not value:
        return []
    
    if isinstance(value, list):
        return value
    
    values = []
    for v in value.split(','):
        values.append(v.strip())
    return values

def from_env(key, default=None, cast=None):
    
    value = os.environ.get(key, default)
    
    if not cast:
        return value
    elif cast == 'list':
        return to_list(value) 
    elif cast == 'int':
        return int(value)
    elif cast == 'float':
        return float(value)
    elif cast == 'bool':
        value = str(value)
        if value.lower() not in _BOOLEANS:
            raise ValueError('Not a boolean: %s' % value)
        return _BOOLEANS[value.lower()]
    else:    
        return str(value)

def str_type(value):
    return str(type(value))

def is_true(value=None):
    """
    {% if is_true(value) %}...{% endif %}
    """
    if None:
        return False
    
    if value is True:
        return True
    elif value is False:
        return False
    
    if str(value).lower() in ('true', '1', 'y', 'yes'): return True
    
    return False    

def is_false(value=None):
    """
    {% if is_false(value) %}...{% endif %}
    """
    if None:
        return True

    if value is False:
        return True
    elif value is True:
        return False
    
    if str(value).lower() in ('false', '0', 'n', 'no'): return True
    
    return False    

def hostname():
    import socket
    return socket.gethostname()

def cpu_count():
    import multiprocessing
    return multiprocessing.cpu_count()

def TODOget_public_ip():
    """Get public IP address."""
    data = str(urlopen('http://www.realip.info/api/p/realip.php').read())
    return data.split('"')[3]

def first_ip(**kwargs):
    return socket.gethostbyname(socket.gethostname())

"""
fqdn: renvoyé par python -c "import socket; print socket.gethostname()"
ns397840.ip-37-187-147.eu ou par envoy sur hostname -f
"""

MY_FUNCTIONS = {
    'FIRST_IP': first_ip
}
    