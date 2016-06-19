# -*- coding: utf-8 -*-

import unittest

import os
from six import StringIO
import six

from tplconfig.config_from import config_from_yaml

HOME_ENV = os.environ.get('HOME', None)

CONFIG = """
postfix:
  enable: true
  home: ENV_HOME
"""
    
def test_config_yaml():
    fileobj = StringIO(CONFIG)
    result = config_from_yaml(fileobj=fileobj, silent=True, upper_only=False, parse_env=False)
    fileobj.close()    
    assert "postfix" in result
    assert result['postfix']['enable'] is True 
    
#@unittest.skip("TODO")
def test_config_yaml_with_env():
    #assert False, "Not Implemented"
    fileobj = StringIO(CONFIG)
    result = config_from_yaml(fileobj=fileobj, silent=True, upper_only=False, parse_env=True)
    fileobj.close()
    print(result)
    assert result['postfix']['home'] == HOME_ENV    

def myprint(d, newdict):
    for k, v in six.iteritems(d.copy()):
        if isinstance(v, dict):
            myprint(v, newdict)
        else:
            newdict[k] = v
          #print "myprint : {0} : {1}".format(k, v)
          
def myprint2(d):
    for k, v in six.iteritems(d):
        if isinstance(v, dict):
            yield {k:myprint2(v)}
        else:
            yield {k:v}
            
def myprint3(kwargs):
    values = {}
    
    for k, v in six.iteritems(kwargs):
        if isinstance(v, dict):
            values[k] = myprint3(v)
        else:
            if v.startswith("ENV_"):
                values[k] = "REPLACEENV"
            else:
                values[k] = v
    
    return values        

#@unittest.skip("TODO")
def test_dict_recursif():
    #assert False, "Not Implemented"
    """
    types
    """
    values = {
        'postfix': {
            'key': 'value',
            'keydict': {
                'v1': "ENV_XXX",
                'v2': {
                    'sub_v2': "ENV_YYY"
                }
            } 
        }
    }
    newdict = {}

    print("")
    print("--------------------")
    new_values = myprint3(values)
    
    print("new_values : ", new_values.keys())
    
    for k, v in new_values.items():
        print(k, v)
    print("--------------------")
    
    import pprint
    #print "newdict : "
    #pprint.pprint(newdict)
    """
    {'key': 'value', 'v1': 'MOI'}    
    """