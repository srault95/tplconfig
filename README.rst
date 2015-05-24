tplconfig
=========

Configuration par template jinja à partir d'une source (yaml, json, http, python, environnement)

|Build Status| |pypi downloads| |pypi version| |pypi licence|

Fonctionnalités
---------------

- Templates Jinja2
- Configuration multi-sources (yaml, json, http, python, env)
- Stockage de la configuration dans un cache permanent (30 secondes)

Exemples
--------

::

    $ tplconfig -C yaml:///config.yml -i /etc/postfix/main.cf.tpl -o /etc/postfix/main.cf
    
    # Pareil à ci-dessus car le nom et chemin du fichier final est déduit du template:    
    $ tplconfig -C yaml:///config.yml -i /etc/postfix/main.cf.tpl
    
    # Chargement par un package python stockant les templates
    $ tplconfig -C http://localhost/config.yml -t mypackage \
       -i postfix/main.cf.tpl -o /etc/postfix/main.cf


Chargement de la configuration
------------------------------

**Formats implémentés:**

- yaml: yaml://<chemin_relatif_ou_absolu>
- json: json://<chemin_relatif_ou_absolu>
- http / https (REST json): http://uri
- module python: python://mypackage.mymodule
- class python: python://mypackage.mymodule:MyClass 
- etcd: (en cours...)

Choix par le paramètre -C FORMAT:// ou par la variable d'environnement : SETTINGS=FORMAT://<chemin>

Templates Jinja2
----------------

- Un template peut se trouver dans un package ou dans un répertoire.

Dans un répertoire
::::::::::::::::::

::

    /etc/postfix/main.cf.tpl

Structure d'un package python avec des templates
::::::::::::::::::::::::::::::::::::::::::::::::

- Le package doit être installé ou disponible dans PYTHONPATH

::

    mypackage
        __init__.py
        templates/postfix.conf.tpl
        templates/system/resolv.conf.tpl


Variables d'environnement une configuration
-------------------------------------------

Si vous utiliser ENV_MYVAR comme valeur, tplconfig cherchera dans l'environnement la variable 
MYVAR et l'utilisera en remplacement de ENV_MYVAR

**Exemple avec une configuration YAML:**

::

    hosts:
        - 1.1.1.1
        - 2.2.2.2
    hostname: ENV_HOSTNAME
        
**La configuration deviendra:**

::

    # En admettant que votre HOSTNAME renvoi mx1

    {
        'hosts': ['1.1.1.1', '2.2.2.2'],
        'hostname': 'mx1'
    }


Environnement
-------------

TPLCONFIG_SETTINGS
::::::::::::::::::

default: yaml://config.yml

TPLCONFIG_PACKAGE
:::::::::::::::::

default: None

Fonctions incluses dans les templates
-------------------------------------

cpu_count
:::::::::

- Renvoi en valeur numérique, le nombre de processeurs disponibles

::

    {{ cpu_count }}

from_env
::::::::

- Charge le contenu d'une variable d'environnemnt

::

    {{ from_env('MY_VAR') }}

    {{ from_env('MY_VAR', 'mydefaultvalue') }}

    {{ from_env('MY_VAR', '123', cast='int') }}

Transformations de type pour les variables d'environnement (par défaut: aucun)

::

    cast='str'

    cast='int'

    cast='float'

    cast='bool'

    cast='list'
        

.. |Build Status| image:: https://travis-ci.org/srault95/tplconfig.svg?branch=master
   :target: https://travis-ci.org/srault95/tplconfig
   :alt: Travis Build Status
   
.. |pypi downloads| image:: https://img.shields.io/pypi/dm/tplconfig.svg
    :target: https://pypi.python.org/pypi/tplconfig
    :alt: Number of PyPI downloads
    
.. |pypi version| image:: https://img.shields.io/pypi/v/tplconfig.svg
    :target: https://pypi.python.org/pypi/tplconfig
    :alt: Latest Version

.. |pypi licence| image:: https://img.shields.io/pypi/l/tplconfig.svg
    :target: https://pypi.python.org/pypi/tplconfig
    :alt: License

