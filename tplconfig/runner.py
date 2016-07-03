# -*- coding: utf-8 -*-

import time
import os
import sys
import argparse
from pprint import pprint as pp 

from tplconfig.jinja_config import Fatal, process_file

from tplconfig.config_from import Config, export_config

def main():
    
    parser = argparse.ArgumentParser(
        description='jinja2 template rendering'
    )

    parser.add_argument('-C', '--config', 
                        default=os.environ.get('TPLCONFIG_SETTINGS', 'yaml://config.yml'), 
                        dest='config_path',
                        help='Config file path. [default: %(default)s]'
                        )

    parser.add_argument('-i', '--input-file',
                        dest='input_file',
                        help='Input filepath.'
    )
    
    parser.add_argument('-o', '--output-file',
                        dest='output_file', 
                        default=None,
                        help='Output filepath or - for stdout.')

    parser.add_argument('-t', '--templates-package',
                        dest='templates_package',
                        default=os.environ.get('TPLCONFIG_PACKAGE', None), 
                        help='Template package (search in PYTHONPATH)'
    )
    
    parser.add_argument('--allow-missing', action='store_true',
                        help='Allow missing variables. By default, envtpl will die with exit '
                        'code 1 if an environment variable is missing'
    )
    
    #parser.add_argument('--environ', action="store_true",
    #                    dest='parse_env',
    #                    help='Parse environment')

    parser.add_argument('--cache-path',
                        dest='config_cache',
                        default='/tmp/tplconfig.cache.yml',
                        help='Store loaded config to cache file. [default: %(default)s]'
    )

    parser.add_argument('--cache-maxtime',
                        dest='cache_maxtime',
                        default=30,
                        type=int,
                        help='Expire cache time (seconds). [default: %(default)s]'
    )

    parser.add_argument('--no-cache', dest="no_cache", action="store_true")

    parser.add_argument('-D', '--debug', action="store_true")

    parser.add_argument('-S', '--show-config', 
                        dest="display_config", 
                        action="store_true",
                        help="Show config only (for test)")
    
    args = parser.parse_args()

    config_path = args.config_path
    
    if not args.no_cache and os.path.exists(args.config_cache):
        mstat = os.stat(args.config_cache)
        if int(time.time() - mstat.st_mtime) < args.cache_maxtime: 
            sys.stdout.write("load settings from cache\n")
            config_path = "yaml://%s" % args.config_cache
    
    kwargs = Config(config_from=config_path,
                    silent=False, 
                    upper_only=False, 
                    parse_env=True #args.parse_env
                    ).items
    
    if args.debug or args.display_config:
        print("")
        print("---------------------------------------------------")    
        pp(kwargs)
        print("---------------------------------------------------")
    
    if args.display_config:
        sys.exit(0)    
    
    try:
        if not args.no_cache:
            export_config(config=kwargs, export_path=args.config_cache, format='yaml')
        
        process_file(templates_package=args.templates_package,
                     input_filename=args.input_file, 
                     output_filename=args.output_file,
                     kwargs=kwargs,
                     die_on_missing_variable=not args.allow_missing,
                     debug=args.debug)
        
    except (Fatal, IOError) as e:
        sys.stderr.write('Error: %s\n' % str(e))
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    """
    
    python -m tplconfig.runner -C yaml://tplconfig/tests/resources/config.yml -i tplconfig/tests/resources/config.conf.tpl -o - -D
    
    # création du fichier final si pas de -o -
    tplconfig/tests/resources/config.conf    
    
    # pour un template dans un package déclaré dans PYTHONPATH
    export TPLCONFIG_PACKAGE=tplconfig.tests.resources.templates_package
    python -m tplconfig.runner -i conf/postfix/main.cf.tpl -C yaml://config.default.yml

    # ou:
    python -m tplconfig.runner -t tplconfig.tests.resources.templates_package -i conf/postfix/main.cf.tpl -C yaml://config.default.yml
    
    # pour tester un seul template et afficher sur stdout
    python -m tplconfig.runner -i apps/nginx/conf/nginx.conf.tpl -C yaml://config.default.yml -o -
        
    """
    main()
