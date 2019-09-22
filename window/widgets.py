from .utils import patch_tk_widget
from .tkhighlight import SyntaxHighlightText
from tkinter import (
    Tk, Canvas, Button, Label, Entry
)

Canvas = patch_tk_widget(Canvas)
Button = patch_tk_widget(Button)
Label = patch_tk_widget(Label)
Entry = patch_tk_widget(Entry)


class WidgetsMixIn:
    def init_widgets(self):
        _dir = set(dir(self))

        self.imagepreview = Canvas(self)
        self.codeblock = SyntaxHighlightText(self)

        self.seedlabel = Label(self, text="Seed:")
        self.seedinput = Entry(self)
        self.seedrandom = Button(self, text="Random")
        self.execbutton = Button(self, text="Execute")

        self.loadcodebutton = Button(self, text="Load code")
        self.savecodebutton = Button(self, text="Save code")
        self.loadimagebutton = Button(self, text="Load IMG")
        self.saveimagebutton = Button(self, text="Save IMG")
        self.resetimagebutton = Button(self, text="Reset")
        self.profiler_canvas = Canvas(self)
        self.statusbar = Label(self, text="--- --- idle --- ---")

        _widgets_list = set(dir(self)) ^ _dir
        _widgets_list = map(lambda k: [k, getattr(self, k)], _widgets_list)
        self._widgets_list = dict(_widgets_list)

        self.profiler_canvas.create_text((10, 120),
                                         text="Waiting for first execution...",
                                         fill="#fafafa",
                                         font="monospace 8",
                                         tags=("total-time",),
                                         anchor="nw")
        self.profiler_canvas.create_text((10, 130),
                                         text="Image dimensions: N/A",
                                         fill="#fafafa",
                                         font="monospace 8",
                                         tags=("image-dims",),
                                         anchor="nw")
        self.profiler_canvas.create_text((10, 140),
                                         text="Image mode: N/A",
                                         fill="#fafafa",
                                         font="monospace 8",
                                         tags=("image-mode",),
                                         anchor="nw")

        self._configure_widgets()
        self.update()
        self._place_widgets()

    def _configure_widgets(self):
        self.seedrandom.config(fg="#faaffa", activeforeground="#fa78fa")
        self.execbutton.config(fg='#affaaf', activeforeground='#78fa78')
        self.loadcodebutton.config(fg='#afaffa', activeforeground='#7878fa')
        self.savecodebutton.config(fg='#faafaf', activeforeground='#fa7878')
        self.loadimagebutton.config(fg='#affafa', activeforeground='#78fafa')
        self.saveimagebutton.config(fg='#fafaaf', activeforeground='#fafa78')
        self.resetimagebutton.config(fg='#fafafa', activeforeground='#afafaf')
        self.statusbar.config(fg='#787878', activeforeground='#afafaf')

    def _place_widgets(self):
        width, height, top, l = self.get_geometry()
        half_width = width // 2
        l, r = half_width, width - half_width
        sep = height - 200

        self.imagepreview.place(x=0, y=0, width=l, height=sep)
        self.imagepreview.config(width=l, height=sep)
        self.codeblock.place(x=l, y=0, width=r, height=sep)

        self.seedlabel.place(x=0, y=sep, width=50, height=25)
        self.seedinput.place(x=50, y=sep, width=l - 150, height=25)
        self.seedrandom.place(x=l - 100, y=sep, width=100, height=25)

        self.execbutton.place(x=l, y=sep, width=100, height=50)
        self.loadcodebutton.place(x=l, y=sep + 50,  width=100, height=25)
        self.savecodebutton.place(x=l, y=sep + 75,  width=100, height=25)
        self.loadimagebutton.place(x=l, y=sep + 100, width=100, height=25)
        self.saveimagebutton.place(x=l, y=sep + 125, width=100, height=25)
        self.resetimagebutton.place(x=l, y=sep + 150, width=100, height=25)
        self.profiler_canvas.place(x=l + 100, y=sep, width=r - 100, height=200)
        self.statusbar.place(x=0, y=sep + 175, width=l, height=25)
