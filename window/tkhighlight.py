from tkinter import (
    Text, Frame, Scrollbar
)
from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import PythonLexer
from .utils import patch_tk_widget

Text = patch_tk_widget(Text)
Frame = patch_tk_widget(Frame)
Scrollbar = patch_tk_widget(Scrollbar)


class TKFmt(Formatter):
    def __init__(self, **options):
        super().__init__(**options)
        self._textw = None

    @property
    def textw(self):
        return self._textw

    @textw.setter
    def textw(self, val):
        self._textw = val
        self.styles = {}
        self._textw.tag_configure('err', foreground='#ff0000')
        for token, style in self.style:
            name = repr(token)
            if not style.get('color'):
                continue
            self._textw.tag_configure(f'tag_{name}',
                                      foreground='#' + style['color'])
            self.styles[token] = [name, style]

    def format(self, tokensource, outf):
        for token_type, value in tokensource:
            while token_type not in self.styles:
                if token_type.parent:
                    token_type = token_type.parent
                else:
                    break
            name, style = self.styles.get(token_type, ('err', None))
            self._textw.insert('end', value, (f'tag_{name}'))


class SyntaxHighlightText(Frame):
    IGNORED_CHARS = ['up', 'down', 'left', 'right', 'tab', 'return', 'space']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._master = args[0]
        self._bar_y = Scrollbar(self)
        self._bar_y.pack(side="right", fill="y")
        self._text = Text(self, yscrollcommand=self._bar_y.set)
        self._text.pack()
        self._text.bind('<KeyRelease>', self.on_keyup)
        self._text.config(font='monospace 10')
        self._bar_y.config(command=self._text.yview)

    def highlight(self, txt):
        formatter = TKFmt(style="monokai")
        formatter.textw = self._text
        highlight(txt, PythonLexer(), formatter)

    def on_keyup(self, event):
        if (event.char.isprintable()
                and event.keysym.lower() not in self.IGNORED_CHARS):
            self.redraw()

    def redraw(self):
        pos = self._text.index('insert')
        txt = self._text.get('1.0', 'end')
        self._text.delete('1.0', 'end')
        self.highlight(txt)
        self._text.mark_set('insert', pos)
        self._text.see(pos)
