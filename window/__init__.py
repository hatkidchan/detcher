
from tkinter import Tk
from .widgets import WidgetsMixIn
from .binders import BindersMixIn
from .utils import FileDialogMixIn, patch_tk_widget
from .callbacks import CallbacksMixIn
from .adaptive import AdaptiveMixIn
from utils.glitcher import mon as gl_monitor


Tk = patch_tk_widget(Tk)


class Window(Tk,
             WidgetsMixIn,
             BindersMixIn,
             AdaptiveMixIn,
             CallbacksMixIn,
             FileDialogMixIn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gl_monitor._window = self
