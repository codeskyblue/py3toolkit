#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Sun Jan 29 2023 15:55:06 by codeskyblue

Clone of [sshw](https://github.com/yinheli/sshw) written in Python

Refs:
- https://python-prompt-toolkit.readthedocs.io/en/master/
- sshpass in python https://gist.github.com/jlinoff/bdd346ffadc226337949
"""

import typing
from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin
from prompt_toolkit import HTML, Application, print_formatted_text
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import FormattedText
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
    user: str
    host: str
    port: int = 22
    keypath: typing.Optional[str] = None
    password: typing.Optional[str] = None
    callback_shells: typing.Optional[typing.List[str]] = None
    children: typing.Optional[typing.List['HostConfig']] = None


# The style sheet.
style = Style.from_dict({
    'active': 'red',
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
            if self._active_index == index:
                host_windows.append(Window(content=FormattedTextControl(HTML(f"  ➤ <cyan>{config.name}</cyan> <gray>{config.user}@{config.host}</gray>")), height=1))
            else:
                host_windows.append(Window(content=FormattedTextControl(HTML(f"    <gray>{config.name} {config.user}@{config.host}</gray>")), height=1))
        return host_windows

    def _up_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        self.set_active_index(index - 1)
    
    def _down_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        self.set_active_index(index + 1)
    
    def _enter_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        event.app.exit(self._host_configs[index])
    
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

def main():
    hosts_container = SelectContainer([mymac, pc001, pc002])
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
        if host_config.password:
            cmds.insert(0, ["sshpass", "-p", host_config.password])
        print(" ".join(cmds))


if __name__ == '__main__':
    main()