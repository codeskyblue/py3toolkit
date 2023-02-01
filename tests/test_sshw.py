#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Wed Feb 01 2023 14:38:55 by codeskyblue
"""

from py3toolkit.sshw import HostConfig
import yaml

test_config = """
- name: mymac
  password: hahaha
  children:
    - name: pc001
      user: anonymous
      host: example.com
    - name: pc002
      user: kitty
      password: 123123
      host: kitty.example.com
      callback-shells:
      - {cmd: "echo hello world"}
"""

def test_load_host_config():
    host_config = HostConfig.schema().load(yaml.safe_load(test_config), many=True)
    assert len(host_config) == 1
    assert host_config[0].name == "mymac"
    assert host_config[0].password == "hahaha"
    assert len(host_config[0].children) == 2
    assert host_config[0].children[0].name == "pc001"