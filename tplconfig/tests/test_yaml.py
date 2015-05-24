# -*- coding: utf-8 -*-

import unittest

import os
from StringIO import StringIO

from tplconfig.config_from import config_from_yaml

CONFIG = """
postfix:
  enable: true
  myhostname: ENV_TEST_HOSTNAME
  banner: $myhostname
"""
    
def test_config_yaml():
    fileobj = StringIO(CONFIG)
    result = config_from_yaml(fileobj=fileobj, silent=True, upper_only=False, parse_env=False)
    fileobj.close()    
    assert "postfix" in result
    assert result['postfix']['enable'] is True 
    
@unittest.skip("TODO")
def test_config_yaml_with_env():
    assert False, "Not Implemented"
    os.environ['TEST_HOSTNAME'] = 'MYHOST'
    fileobj = StringIO(CONFIG)
    result = config_from_yaml(fileobj=fileobj, silent=True, upper_only=False, parse_env=True)
    fileobj.close()    
    assert "postfix" in result
    assert result['postfix']['myhostname'] == 'MYHOST' 

def myprint(d, newdict):
    for k, v in d.copy().iteritems():
        if isinstance(v, dict):
            myprint(v, newdict)
        else:
            newdict[k] = v
          #print "myprint : {0} : {1}".format(k, v)
          
def myprint2(d):
    for k, v in d.iteritems():
        if isinstance(v, dict):
            yield {k:myprint2(v)}
        else:
            yield {k:v}
          
@unittest.skip("TODO")
def test_dict_recursif():
    assert False, "Not Implemented"
    """
    types
    """
    values = {
        'postfix': {
            'key': 'value',
            'keydict': {
                'v1': "MOI"
            } 
        }
    }
    newdict = {}
    #myprint(values, newdict)
    #myprint2(values, newdict)
    print ""
    print "--------------------"
    for v in myprint2(values):
        print v
    print "--------------------"
    
    import pprint
    #print "newdict : "
    #pprint.pprint(newdict)
    """
    {'key': 'value', 'v1': 'MOI'}    
    """