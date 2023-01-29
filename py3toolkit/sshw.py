#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Sun Jan 29 2023 15:55:06 by codeskyblue

Clone of [sshw](https://github.com/yinheli/sshw) written in Python

Refs:
- https://python-prompt-toolkit.readthedocs.io/en/master/
"""

from prompt_toolkit import Application, HTML, print_formatted_text
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.containers import VSplit, HSplit, FloatContainer, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout import VerticalAlign

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active_index = 0

    def _up_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        self.set_active_index(index - 1)
    
    def _down_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        self.set_active_index(index + 1)
    
    def _enter_hook(self, event: KeyPressEvent):
        index = self.get_active_index()
        event.app.exit(index)
    
    def get_active_index(self):
        return self._active_index
    
    def set_active_index(self, index):
        self._active_index = index % len(self.children)
        self._update_active()
    
    def _update_active(self):
        for i, child in enumerate(self.children):
            if i == self._active_index:
                child.style = 'class:active'
            else:
                child.style = ''

    def register_key_bindings(self, kb: KeyBindings):
        for key in ['up', 'k']:
            kb.add(key)(self._up_hook)
        for key in ['down', 'j']:
            kb.add(key)(self._down_hook)
        kb.add(Keys.Enter)(self._enter_hook)

buffer1 = Buffer()  # Editable buffer.

menu_items = []
for name in host_names:
    menu_items.append(Window(content=FormattedTextControl(HTML("> " + name)), height=1))
menu_items[0].style = 'class:active'

hosts_container = SelectContainer(menu_items)
hosts_container.register_key_bindings(kb)


root_container = HSplit([
    Window(content=FormattedTextControl(HTML('<gray>Use the arrow keys to navigate: ↓ ↑ → ←  and / toggles search</gray>')), height=1),
    Window(content=FormattedTextControl(HTML('<lightgreen>✨ Select host</lightgreen>')), height=1),
    hosts_container,
])

layout = Layout(root_container)

def main():
    app = Application(layout=layout, style=style, key_bindings=kb, full_screen=True)
    print(app.run())


if __name__ == '__main__':
    main()