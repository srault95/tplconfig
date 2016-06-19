# -*- coding: utf-8 -*-

import os
from six import StringIO

from jinja2 import TemplateNotFound

from . import resources

templates = resources.__path__[0]

from tplconfig.jinja_config import process_file, Fatal

def test_load_template():
    config = dict(test="TEST")
    tmpl = os.path.abspath(os.path.join(templates, 'config.conf.tpl'))
    fileobj = StringIO()
    process_file(input_filename=tmpl, output_fileobj=fileobj, 
                          kwargs=dict(config=config), 
                          die_on_missing_variable=False)
    value = fileobj.getvalue()
    fileobj.close()
    assert value  == "TEST"
    
def test_load_template_package():
    config = dict(test="TEST")

    fileobj = StringIO()
    
    process_file(templates_package='tplconfig.tests.resources.templates_package', 
                 input_filename='config.conf.tpl', 
                 output_fileobj=fileobj, 
                 kwargs=dict(config=config))
            
    value = fileobj.getvalue()
    fileobj.close()
    assert value  == "TEST"

def test_bad_value_in_template():
    tmpl = os.path.abspath(os.path.join(templates, 'badvalue.tpl'))
    try:
        process_file(input_filename=tmpl, 
                     output_filename='-', 
                     kwargs=dict())    
        assert False, "exception not raised"
    except Fatal as err:
        assert str(err) == "'config' is undefined"
    
def test_template_not_found():
    try:
        process_file(templates_package='tplconfig.tests.resources.templates_package', 
                     input_filename='notfoundtemplate.html', 
                     output_filename='-', 
                     kwargs=dict())    
        assert False, "exception not raised"
    except TemplateNotFound as err:
        assert err.templates == ['notfoundtemplate.html']

def test_templates_package_not_found():
    try:
        process_file(templates_package='tplconfig.bad_package', 
                     input_filename='notfoundtemplate.html', 
                     output_filename='-', 
                     kwargs=dict())    
        assert False, "exception not raised"
    except ImportError:
        pass
