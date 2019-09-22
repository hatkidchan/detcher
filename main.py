#!/usr/bin/python3
from window import Window
from utils.helper import main as helper_run
import argparse

__author__ = "undefinedvalue0103@gitlab.com"
__version__ = "v. 0.2 beta"

class dataobject(object):
    pass


class App(Window):
    def __init__(self):
        super().__init__()
        self.title(f"Detcher-GUI {__version__}")
        self.shared = dataobject()
        self.config(width=800, height=500)
        self.init_widgets()
        self.bind_handlers()
        self.begin_loop()
        self.post_init()


parser = argparse.ArgumentParser("detcher",
                                 description="Python image glitching tool")
parser.add_argument("--IS-HELPER",
                    dest="IS_HELPER",
                    action="store_true")
parser.add_argument("--version",
                    action="version",
                    version=f"%(prog)s {__version__}")
parser.add_argument("--tmp-dir",
                    dest="hl_tmp_dir")

args = parser.parse_args()

if args.IS_HELPER:
    helper_run(args)
else:
    app = App()
    app.mainloop()
