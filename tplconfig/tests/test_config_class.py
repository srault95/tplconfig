# -*- coding: utf-8 -*-

import unittest
import os

from tplconfig.config_from import Config

from . import resources

RESOURCES = os.path.abspath(os.path.dirname(resources.__file__))
 
yaml_config = os.path.realpath(os.path.join(RESOURCES, 'config.yml'))
json_config = os.path.abspath(os.path.join(RESOURCES, 'config.json'))
#python_config = os.path.abspath(os.path.join(RESOURCES, 'config.yml'))

class ConfigTestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
        
    def test_config_class(self):
        
        config = Config()

        self.assertEquals(config._loaded, False)
        
        self.assertEquals(config._config_from, 'env://')
        
        self.assertIsNotNone(config._contenair)
        
        self.assertEquals(len(config._contenair), 0)
        
        self.assertIsNone(config.get('TEST', None))
        
    def test_config_load(self):
        
        config = Config(config_from="yaml://%s" % yaml_config)

        self.assertEquals(config._loaded, False)
        self.assertEquals(len(config._contenair), 0)

        config.load()
        
        self.assertEquals(config._loaded, True)
        self.assertIsNotNone(config._contenair)        
        
        self.assertIsNotNone(config.get('var_str', None))
        
        config = Config(config_from="yaml://%s" % yaml_config)        
        self.assertIsNotNone(config('var_str', None))
        
    def test_config_from_object(self):
        
        config = Config(config_from="python://tplconfig.tests.resources.dummy")
        self.assertEquals(config('VAR4', None), 'var4')
        self.assertIsNone(config('bad_var', None))
        
        config = Config(config_from="python://tplconfig.tests.resources.dummy:Test1")
        self.assertEquals(config('VAR1', None), 'var1')
        
        config = Config(config_from="python://tplconfig.tests.resources.dummy:Test2")
        self.assertEquals(config('VAR1', None), 'var1')

    def test_config_from_env(self):
        
        config = Config(config_from="env://")
        self.assertTrue(len(config.items) > 0)
        #self.assertEquals(config('TPLCONFIG', None), 'var1')

        