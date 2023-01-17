#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Fri Jan 13 2023 20:57:37 by codeskyblue
"""

import subprocess
import sys
import pathlib

simple_cfgpath = pathlib.Path(__file__).parent.joinpath("testdata/test-supervisor.yml")
complex_cfgpath = pathlib.Path(__file__).parent.joinpath("testdata/group-supervisor.yml")

def test_main():
    p = subprocess.run([sys.executable, "-m", "py3toolkit.gen_supervisor_conf", "-c", str(simple_cfgpath)], capture_output=True)
    assert b'program:threebody' in p.stdout
    assert b'program:groundfire' in p.stdout
    assert b'groups:' not in p.stdout

    p = subprocess.run([sys.executable, "-m", "py3toolkit.gen_supervisor_conf", "-c", str(complex_cfgpath)], capture_output=True)
    assert b"[group:foo]\nprograms=foo-bar,foo-ai" in p.stdout
    assert b"[program:foo-bar]" in p.stdout
    assert b"[program:foo-ai]" in p.stdout