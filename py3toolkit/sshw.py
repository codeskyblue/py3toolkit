#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Sun Jan 29 2023 15:55:06 by codeskyblue

Clone of [sshw](https://github.com/yinheli/sshw) written in Python

Refs:
- https://python-prompt-toolkit.readthedocs.io/en/master/
- sshpass in python https://gist.github.com/jlinoff/bdd346ffadc226337949
"""

import dataclasses
import yaml
import pathlib
import typing
from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, config as dconfig
from prompt_toolkit import HTML, Application, print_formatted_text
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import VerticalAlign
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style


@dataclass
class HostConfig(DataClassJsonMixin):
    name: str
    port: int = 22
    host: typing.Optional[str] = None
    user: typing.Optional[str] = None
    keypath: typing.Optional[str] = None
    password: typing.Optional[typing.Union[str, int]] = None
    callback_shells: typing.Optional[typing.List[dict]] = dataclasses.field(metadata=dconfig(field_name="callback-shells"), default=None)
    children: typing.Optional[typing.List["HostConfig"]] = None

    def get_password(self) -> typing.Optional[str]:
        if self.password is None:
            return None
        return str(self.password)


# The style sheet.
style = Style.from_dict({
    'active': 'red',
    'name': 'cyan',
    'bbb': '#44ff00 italic',
})

kb = KeyBindings()

@kb.add('q')
@kb.add('c-c')
def exit_(event: KeyPressEvent):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()

host_names = ["root@20220122", "pi@raspberry", "dummy"]

class SelectContainer(HSplit):
    def __init__(self, host_configs: typing.List[HostConfig]):
        self._host_configs = host_configs
        self._active_index = 0
        super().__init__(self._gen_host_windows())
    
    def _gen_host_windows(self):
        host_windows = []
        for index, config in enumerate(self._host_configs):
            prefix = "" if config.children else f" <gray>{config.user}@{config.host}</gray>"
            if self._active_index == index:
                html_text = "  ➤ " + f"<name>{config.name}</name>" + prefix
            else:
                html_text = "    " + f"<gray>{config.name}</gray>" + prefix
            host_windows.append(Window(content=FormattedTextControl(HTML(html_text)), height=1))
        return host_windows

    def _up_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        self.set_active_index(index - 1)
    
    def _down_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        self.set_active_index(index + 1)
    
    def _enter_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        config = self._host_configs[index]
        if config.children:
            if config.name == "-parent-":
                self._host_configs = config.children
            else:
                parent = HostConfig(name="-parent-", children=self._host_configs[:])
                self._host_configs = [parent] + config.children
            self.set_active_index(0)
        else:
            event.app.exit(config)
    
    def get_active_index(self):
        return self._active_index
    
    def set_active_index(self, index):
        self._active_index = index % len(self.children)
        self._update_active()
    
    def _update_active(self):
        self.children = self._gen_host_windows()

    def register_key_bindings(self, kb: KeyBindings):
        for key in ['up', 'k']:
            kb.add(key)(self._up_hook)
        for key in ['down', 'j']:
            kb.add(key)(self._down_hook)
        kb.add(Keys.Enter)(self._enter_hook)

buffer1 = Buffer()  # Editable buffer.


mymac = HostConfig(name="mymac", user="codeskyblue", host="127.0.0.1")
pc001 = HostConfig(name="pc001", user="anonymous", host="example.com")
pc002 = HostConfig(name="pc002", user="kitty", host="kitty.example.com")

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

def load_config() -> typing.List[HostConfig]:
    p = pathlib.Path("~/.sshw.yml").expanduser()
    return HostConfig.schema().load(yaml.safe_load(p.read_bytes()), many=True)
    # return HostConfig.schema().load(yaml.safe_load(test_config), many=True)


def main():
    host_configs = load_config()
    hosts_container = SelectContainer(host_configs) #[mymac, pc001, pc002])
    hosts_container.register_key_bindings(kb)

    root_container = HSplit([
        Window(content=FormattedTextControl(HTML('<gray>Use the arrow keys to navigate: ↓ ↑ → ←  and / toggles search</gray>')), height=1),
        Window(content=FormattedTextControl(HTML('<lightgreen>✨ Select host</lightgreen>')), height=1),
        hosts_container,
    ])

    layout = Layout(root_container)

    app = Application(layout=layout, style=style, key_bindings=kb, full_screen=True)
    host_config = app.run()
    if host_config:
        print(host_config)
        cmds = ["ssh"]
        if host_config.port != 22:
            cmds.extend(["-p", str(host_config.port)])
        cmds.extend([f"{host_config.user}@{host_config.host}"])
        if host_config.get_password():
            cmds = ["sshpass", "-p", host_config.get_password()] + cmds
        print(cmds)
        print(" ".join(cmds))


if __name__ == '__main__':
    main()