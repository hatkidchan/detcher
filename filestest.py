#!/usr/bin/env python3
from tkinter import (
    Tk, Canvas
)
from window.utils import patch_tk_widget
import os
import zlib

Tk = patch_tk_widget(Tk)
Canvas = patch_tk_widget(Canvas)

class dataobject:
    pass

class Window(Tk):
    def __init__(self):
        super().__init__()
        self.config(width=500, height=110)
        self.graph = Canvas(self)
        self.graph.config(width=500, height=110)
        self.graph.pack()
        self.data = dataobject()
        self.data.total_nonempty_lines = 0

    def scan(self, path="."):
        self.data.stat = {}
        self.data.stat_с = {}
        self.clear_graph()
        for (relpath, folders, files) in os.walk(path):
            if ".scanignore" in files:
                continue
            for file in files:
                fullpath = os.path.join(relpath, file)
                realpath = os.path.realpath(fullpath)

                if realpath == __file__:
                    continue

                name, ext = os.path.splitext(file)
                if ext == ".py":
                    self.data.total_nonempty_lines += len(open(fullpath).readlines())
                stat = os.stat(fullpath)
                size = stat.st_size
                print(f"{realpath}: {size}")
                self.data.stat[ext] = self.data.stat.get(ext, 0) + size
                self.data.stat_с[ext] = self.data.stat_с.get(ext, 0) + 1
                self.update_graph()
        print(f"total_nonempty_lines: {self.data.total_nonempty_lines}")

    def clear_graph(self):
        self.graph.delete("pieslice")
        self.graph.delete("text")

    def update_graph(self):
        sizes = dict(self.data.stat)
        canvas = self.graph
        totalsize = sum(sizes.values())
        pos = (5, 5, 105, 105)
        current = 0
        for ext, size in sizes.items():
            if not canvas.find_withtag(f"pie{ext}"):
                colorval = zlib.crc32(ext.encode()) & 0x7f7f7f
                color = "#%.6x" % (colorval + 0x7f7f7f)
                canvas.create_arc(pos, tags=("pieslice", f"pie{ext}"),
                                  fill=color, outline=color)

            angle = 360 * (size / totalsize)
            canvas.itemconfig(f"pie{ext}",
                              start=current,
                              extent=angle or 360)
            current += angle

        data = sorted(sizes.items(), key=lambda c: c[1], reverse=True)
        for i, (ext, size) in zip(range(10), data):
            if not canvas.find_withtag(f"text{ext}"):
                colorval = zlib.crc32(ext.encode()) & 0x7f7f7f
                color = "#%.6x" % (colorval + 0x7f7f7f)
                canvas.create_text((110, 10 + (10 * i)),
                                   text="N/A",
                                   fill=color,
                                   font="monospace 8",
                                   anchor="nw",
                                   tags=("text", f"text{ext}"))
            if size >= 1024 ** 3:
                hs = f"{size / (1024 ** 3):6.2f} G"
            elif size >= 1024 ** 2:
                hs = f"{size / (1024 ** 2):6.2f} M"
            elif size >= 1024 ** 1:
                hs = f"{size / (1024 ** 1):6.2f} k"
            else:
                hs = f"{size:6.2f}  "

            c = self.data.stat_с.get(ext, "N/A")
            top_str = f"{hs}B ({size * 100 / totalsize:5.2f}%) - x{c} *{ext}"
            canvas.itemconfig(f"text{ext}", text=top_str)
            canvas.coords(f"text{ext}", (110, 10 + (10 * i)))

        self.update()

def main():
    wnd = Window()
    wnd.scan()
    wnd.mainloop()

if __name__ == '__main__':
    main()