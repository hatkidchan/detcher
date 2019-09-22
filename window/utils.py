import tkinter.filedialog as filedialog

TK_THEME = {
    'background': '#131313',
    'foreground': '#afafaf',
    'highlightbackground': '#080808',
    'highlightcolor': '#262626',
    'relief': 'flat',
    'troughcolor': '#262626',
    'font': 'monospace 11',
    'borderwidth': 0,
    'selectbackground': '#262626',
    'selectforeground': '#afaffa',
    'activebackground': '#262626',
    'activeforeground': '#ffffff',
    'insertbackground': '#787878',
    'insertofftime': 500,
    'insertontime': 500
}


def patch_tk_widget(widget_class):
    _name = widget_class.__name__

    class subclass(widget_class):
        __real_name__ = _name

        def _initial_config(self):
            for k, v in TK_THEME.items():
                try:
                    self.config({k: v})
                except:
                    pass
            for k, v in getattr(self, "_STYLE", {}).items():
                try:
                    self.config({k: v})
                except:
                    pass

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._initial_config()
    return subclass


class FileDialogMixIn:
    def ask_file_read(self, types=None):
        return filedialog.askopenfilename(master=self, filetypes=types)

    def ask_file_write(self, types=None):
        return filedialog.asksaveasfilename(master=self, filetypes=types)
