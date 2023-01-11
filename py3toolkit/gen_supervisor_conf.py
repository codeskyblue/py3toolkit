#!/usr/bin/env python3
#

"""
Refs:
- https://jinja.palletsprojects.com/en/3.1.x/templates/
- https://stackoverflow.com/questions/39288706/jinja2-load-template-from-string-typeerror-no-loader-for-this-environment-spec

改进型的yaml，支持符号~,增加默认配置redirect_stderr,stopasgroup,killasgroup,directory,user,stdout_logfile_backups=1,environment增加PATH
支持group增加统一前缀

Input
---
- group: liu
  programs:
    - name: threebody
      command: python threebody_engine.py
    - name: balllight
      command: bash balllight.sh
    - name: groundfire
      command: ./server.py
      startsecs: 10
      numprocs: 1
      user: pi # default current user
      directory: / # default current directory
      stopasgroup: true
      killasgroup: true
      redirect_stderr: true
      startsecs: 1
      strip_ansi: false
      stdout_logfile_maxbytes: "10MB"
      stdout_logfile_backups: 1

Output
---
[group:liu]
programs=liu-threebody,liu-balllight,liu-groundfire

[program:liu-threebody]
user=$(whoami)
directory=$(cwd)
numprocs=1
command=.....
stopasgroup=true
killasgroup=true
redirect_stderr=true
environment=A="1",B="2"
startsecs=1
"""

import argparse
import os
import yaml
import pathlib
from pprint import pprint
import typing
from dataclasses import dataclass, field
from dataclasses_json import (CatchAll, DataClassJsonMixin, LetterCase,
                              Undefined)
from jinja2 import Environment, BaseLoader


class _BaseDataClassMixin(DataClassJsonMixin):
    dataclass_json_config = dict()

    def _asdict(self) -> dict:
        """ required called by simplejson """
        return self.to_dict()


@dataclass
class _BaseDataClass(_BaseDataClassMixin):
    pass


@dataclass
class Program(_BaseDataClass):
    name: str
    command: str
    numprocs: int = 1
    user: str = os.environ["USER"]
    directory: str = os.getcwd()
    stopasgroup: bool = True
    killasgroup: bool = True
    redirect_stderr: bool = True
    startsecs: int = 1
    strip_ansi: bool = False
    stdout_logfile_maxbytes: str = "10MB"
    stdout_logfile_backups: int = 1
    # stopsignal: str = "TERM"
    # environment: typing.List[str] = ["PYTHONUNBUFFERED=1"]


@dataclass
class Group(_BaseDataClass):
    programs: typing.List[Program]
    group: str = None
    path: str = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    # priority: int = 999


JINJA_TEMPLATE = """
{% for group in groups %}
[group:{{group.group}}]
programs={{ group.programs | join(",", attribute="name") }}

{% for program in group.programs %}
[program:{{program.name}}]
command={{program.command}}
user={{program.user}}
directory={{program.directory}}
stopasgroup={{program.stopasgroup | lower}}
killasgroup={{program.killasgroup | lower}}
redirect_stderr={{program.redirect_stderr | lower}}
startsecs={{program.startsecs}}
environment=PYTHONUNBUFFERED="1",PATH={{group.path | quote}}
stdout_logfile={{program.directory}}/logs/{{program.name}}.log
stdout_logfile_maxbytes={{program.stdout_logfile_maxbytes}}
stdout_logfile_backups={{program.stdout_logfile_backups}}
{% if program.numprocs > 1 %}
numprocs={{program.numprocs}}
process_name=%(program_name)s_%(process_num)02d
{% endif %}
{% endfor %}
{% endfor %}
"""

def main():
    valid_name = ("supervisor", "supervisor-conf")
    valid_ext = (".yml", ".yaml")
    valid_names = []
    for name in valid_name:
        for ext in valid_ext:
            valid_names.append(name+ext)

    p: pathlib.Path = None
    for guess_path in valid_names:
        _p = pathlib.Path(guess_path)
        if _p.exists():
            p = _p
            break
    if not p:
        raise RuntimeError("No valid conf file found", valid_names)

    with p.open("rb") as f:
        data = yaml.load(f, yaml.SafeLoader)
        groups: typing.List[Group] = Group.schema().load(data, many=True)

    for g in groups:
        if not g.group:
            continue
        for p in g.programs:
            if not p.name.startswith(g.group):
                p.name = g.group + "-" + p.name
                p.command = os.path.expanduser(p.command)
    
    environment = Environment(loader=BaseLoader)
    environment.filters["quote"] = lambda v: '"' + str(v).replace('"', r'\"') + '"'
    rtemplate = environment.from_string(JINJA_TEMPLATE)
    data = rtemplate.render(groups=groups)
    print(data.strip())


if __name__ == "__main__":
    main()
