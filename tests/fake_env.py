import sys
import io
import os
import shutil
import glob

import dotdot

from pyfakefs import fake_filesystem, fake_filesystem_unittest

from pubs.p3 import input, _fake_stdio, _get_fake_stdio_ucontent
from pubs import content, filebroker

# code for fake fs

real_os      = os
real_os_path = os.path
real_open    = open
real_shutil  = shutil
real_glob    = glob
real_io      = io


# redirecting output

def redirect(f):
    def newf(*args, **kwargs):
        old_stderr, old_stdout = sys.stderr, sys.stdout
        stdout = _fake_stdio()
        stderr = _fake_stdio()
        sys.stdout, sys.stderr = stdout, stderr
        try:
            return f(*args, **kwargs), _get_fake_stdio_ucontent(stdout), _get_fake_stdio_ucontent(stderr)
        finally:
            sys.stderr, sys.stdout = old_stderr, old_stdout
    return newf


# Test helpers

# automating input

real_input = input


class FakeInput():
    """ Replace the input() command, and mock user input during tests

        Instanciate as :
        input = FakeInput(['yes', 'no'])
        then replace the input command in every module of the package :
        input.as_global()
        Then :
        input() returns 'yes'
        input() returns 'no'
        input() raises IndexError
     """

    class UnexpectedInput(Exception):
        pass

    def __init__(self, inputs, module_list=tuple()):
        self.inputs = list(inputs) or []
        self.module_list = module_list
        self._cursor = 0

    def as_global(self):
        for md in self.module_list:
            md.input = self
            md._editor_input = self
            md._edit_file = self.input_to_file
            # if mdname.endswith('files'):
            #     md.editor_input = self

    def input_to_file(self, _, path_to_file, temporary=True):
        content.write_file(path_to_file, self())

    def add_input(self, inp):
        self.inputs.append(inp)

    def __call__(self, *args, **kwargs):
        try:
            inp = self.inputs[self._cursor]
            self._cursor += 1
            return inp
        except IndexError:
            raise self.UnexpectedInput('Unexpected user input in test.')


class TestFakeFs(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.rootpath = os.path.abspath(os.path.dirname(__file__))
        self.setUpPyfakefs()
        self.fs.CreateDirectory(self.rootpath)
        os.chdir(self.rootpath)

    def reset_fs(self):
        self._stubber.tearDown()  # renew the filesystem
        self.setUp()
