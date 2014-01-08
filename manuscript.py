#!/usr/bin/env python3
#deps: docopt pathlib
"""Manuscript. Manage your scripts and their dependencies.

Just add a line of the form "#deps: requests docopt pathlib" to your script,
and manuscript will install them in a virtualenv and create a wrapper.

Usage:
  manuscript install SCRIPT [-e ENV -i INTERPRETER -c]
  manuscript check-deps

Options:
  -e ENV          The name of the virtualenv to use
  -i INTERPRETER  Specify the interpreter to use, otherwise,
                  it's guessed from the script's shebang.
  -c              Copy the script so the original can be deleted
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from docopt import docopt

MANUSCRIPT_DIR = Path(os.path.expanduser('~'), '.manuscript')
ENVS_DIR = MANUSCRIPT_DIR['envs']
BIN_DIR = MANUSCRIPT_DIR['bin']
COPIES_DIR = MANUSCRIPT_DIR['script_copies']


def initialize():
    """Checks that everything that should exist exists"""
    subprocess.check_output(['virtualenv', '--version'])
    for path in (MANUSCRIPT_DIR, ENVS_DIR, BIN_DIR, COPIES_DIR):
        if not path.exists():
            path.mkdir()


class Env:
    """One of the virtualenv manipulated by manuscript"""

    def __init__(self, name):
        """Creates a virtualenv with the given name."""
        self.name = name
        if name.startswith('workon:'):
            try:
                workon_dir = Path(os.environ['WORKON_HOME'])
            except KeyError:
                print("'WORKON_HOME' environment variable not found, cannot "
                      "use virtualenv-wrapper env.")
                sys.exit(-1)
            self.dir = workon_dir[name[len('workon:'):]]
        else:
            self.dir = ENVS_DIR[name]

    def created(self):
        return self.dir.exists()

    def ensure_created(self, interpreter):
        """Ensures the env in created. If not, create it with interpreter"""
        if not self.created():
            if self.name.startswith('workon:'):
                print('Cannot create virtualenv-wrapper env, please create it '
                      'yourself with "mkvirtualenv {}"'
                      .format(self.name[len('workon:'):]))
                sys.exit(-1)
            subprocess.check_call(['virtualenv', '-p', interpreter,
                                   str(self.dir)])

    def bin_path(self, bin):
        """Returns the path to a bin in the env"""
        return self.dir['bin'][bin]

    def install(self, pkgs):
        """Install the given packages in the env"""
        if pkgs:
            subprocess.check_call([str(self.bin_path('pip')), 'install']
                                  + pkgs)


def default_env(interpreter):
    """Returns the default env for an interpreter"""
    name = 'default-{}'.format(interpreter)
    env = Env(name)
    env.ensure_created(interpreter)
    return env


SCRIPT_TEMPLATE = """#!/bin/sh
INTERPRETER={}
FILE={}
$INTERPRETER $FILE $*
"""


class Script:
    """One of the scripts manipulated by manuscript"""

    def __init__(self, script, env, copy=False):
        """Creates a script attached to the given environment.  If copy if True,
        first copy this script instead of just linking it"""

        self.path = Path(script).resolve()
        self.name = self.path.name
        self.env = env

        if copy:
            shutil.copy(str(self.path), str(COPIES_DIR))
            print('Copied {} to {}'.format(self.path, COPIES_DIR))
            self.path = COPIES_DIR[self.name]

        if self.name.endswith('.py'):
            self.name = self.name[:-3]

    def dependencies(self):
        """Looks for dependencies of the form "#deps: ..." in the script"""
        with self.path.open() as f:
            for line in f:
                if line.startswith('#deps:'):
                    line = line.replace('#deps:', '').strip()
                    return line.split(' ')
        return []

    def install_deps(self):
        """Install the dependencies of the script"""
        self.env.install(self.dependencies())

    def save(self):
        """Save the script in manuscript's bin dir"""
        self.install_deps()
        with BIN_DIR[self.name].open('w') as f:
            f.write(SCRIPT_TEMPLATE.format(self.env.bin_path('python'),
                                           repr(str(self.path))))
        subprocess.check_call(['chmod', '+x', str(BIN_DIR[self.name])])
        print('Created {}'.format(BIN_DIR[self.name]))


def interpreter_from_shebang(script):
    """Tries to guess the interpreter to use from the shebang of the
    script. Returns None if none is found."""
    with open(script) as f:
        line = next(f)
        if line.startswith('#!'):
            if 'env' in line:
                return line.strip().split('env ')[1]
            else:
                return line.strip().split('/')[-1]
    return None


def script_without_specific_env(script_file, interpreter, copy):
    """Returns a Script created using a fefault interpreter, guess which if
    necessary"""
    interpreter = (interpreter or interpreter_from_shebang(script_file)
                   or 'python')
    env = default_env(interpreter)
    return Script(script_file, env, copy)


def all_scripts():
    """Return all the scripts handled by manuscript"""
    for script in BIN_DIR:
        with script.open() as f:
            lines = f.readlines()
            env = Env(lines[1].split('/')[-3])
            script = lines[2].split("'")[-2]
            yield Script(script, env)


def main():
    args = docopt(__doc__)
    initialize()
    if args['install']:
        if args['-e']:  # A name is given
            env = Env(args['-e'])
            if not env.created():
                interpreter = (args['-i'] or
                               interpreter_from_shebang(args['SCRIPT']) or
                               'python')
                env.ensure_created(interpreter)
            elif args['-i']:
                print('Interpreted provided but env "{}" already '
                      'exists. Ignored'.format(env.name))
            script = Script(args['SCRIPT'], env, args['-c'])
        else:  # No name, use default env
            script = script_without_specific_env(args['SCRIPT'],
                                                 interpreter=args['-i'],
                                                 copy=args['-c'])
        script.save()
    elif args['check-deps']:
        for script in all_scripts():
            script.install_deps()


if __name__ == '__main__':
    main()
