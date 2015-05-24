#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import jinja2

from . import utils

TEMPLATE_GLOBALS = {}
TEMPLATE_GLOBALS['is_true'] = utils.is_true
TEMPLATE_GLOBALS['is_false'] = utils.is_false
TEMPLATE_GLOBALS['hostname'] = utils.hostname
TEMPLATE_GLOBALS['str_type'] = utils.str_type
TEMPLATE_GLOBALS['from_env'] = utils.from_env
TEMPLATE_GLOBALS['cpu_count'] = utils.cpu_count()

class Fatal(Exception):
    pass


def process_file(templates_package=None,
                 input_filename=None, 
                 output_filename=None, 
                 output_fileobj=None, 
                 kwargs=None, 
                 die_on_missing_variable=False,
                 debug=False,
                 backup_before=False):

    """
    python -m tplconfig.runner -i postfix/transport.tpl -C config.default.yml -o -
    python -m tplconfig.runner -i postfix/main.cf.tpl -C config.default.yml -o -

    python -m tplconfig.runner -i /conf/postfix/master.cf.tpl -C config.default.yml -o -
    """
    
    if templates_package:
        loader = jinja2.PackageLoader(templates_package)
        template_path = input_filename
    else:
        loader = jinja2.FileSystemLoader(os.path.abspath(os.path.dirname(input_filename)))
        template_path = os.path.relpath(input_filename, os.path.dirname(input_filename))

    undefined = jinja2.Undefined
    
    if die_on_missing_variable:
        undefined = jinja2.StrictUndefined    
    
    if debug:
        undefined = jinja2.DebugUndefined

    if input_filename and not output_filename:
        """
        >>> ".".join("app.conf.tmpl".split('.')[:-1])
        'app.conf'
        """
        output_filename = ".".join(input_filename.split('.')[:-1])
        if not output_filename:
            raise Fatal('Output filename is empty')
        
    env = jinja2.Environment(loader=loader,
                             extensions=['jinja2.ext.i18n'],
                             autoescape=False, 
                             undefined=undefined,
                             cache_size=0,
                             trim_blocks=True)
    
    env.globals.update(TEMPLATE_GLOBALS)

    try:
        template = env.get_template(template_path)
    except jinja2.TemplateSyntaxError as e:
        raise Fatal('Syntax error on line %d: %s' % (e.lineno, e.message))

    if templates_package:
        try:
            output = template.render(**kwargs)
        except jinja2.UndefinedError as e:
            raise Fatal(e)
    else:
        with open(input_filename, 'r') as f:
            source = f.read()        
        output = _render(source, template, kwargs, undefined)
    
    if output_fileobj:
        output_fileobj.write(output)
        return
    elif output_filename and output_filename != '-':
        with open(output_filename, 'w') as f:
            f.write(output)
    else:
        sys.stdout.write(output)

def _render(source, template, kwargs, undefined):
    if template is None:
        try:
            template = jinja2.Template(source, undefined=undefined)
        except jinja2.TemplateSyntaxError as e:
            raise Fatal('Syntax error on line %d: %s' % (e.lineno, e.message))

    try:
        output = template.render(**kwargs)
    except jinja2.UndefinedError as e:
        raise Fatal(e)

    # jinja2 cuts the last newline
    if source.split('\n')[-1] == '' and output.split('\n')[-1] != '':
        output += '\n'

    return output

