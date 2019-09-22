from PIL import Image, ImageTk, ImageColor
from threading import Thread
from utils.glitcher import (exports as glitcher_exp)
from utils import random_color, get_status_color
import zlib
import random
from subprocess import Popen, PIPE
import tempfile
import sys
import os
import shutil

CODE_FILE_TYPES = [
    ("Python script", "*.py"),
    ("Text file", "*.txt"),
    ("Any file", "*")
]
IMAGE_FILE_TYPES = [
    ("Common image", ("*.bmp", "*.jpeg", "*.jpg", "*.png", "*.webp", "*.gif")),
    ("BMP image", "*.bmp"),
    ("DIB image", "*.dib"),
    ("EPS image", "*.eps"),
    ("GIF image", "*.gif"),
    ("ICNS image", "*.icns"),
    ("ICO image", "*.ico"),
    ("IM image", "*.im"),
    ("JPEG image", ("*.jpg", "*.jpeg")),
    ("MSP image", "*.mps"),
    ("PCX image", "*.pcx"),
    ("PNG image", "*.png"),
    ("PPM image", "*.ppm"),
    ("SGI image", "*.sgi"),
    ("SPIDER image", "*.spi"),
    ("TGA image", "*.tga"),
    ("TIFF image", "*.tiff"),
    ("WebP image", "*.webp"),
    ("XBM image", "*.xbm"),
    ("Any file", "*"),
]


def rm_file(path):
    print("[RM] %r" % path)
    try:
        os.remove(path)
    except:
        pass


class CallbacksMixIn:
    def begin_loop(self):
        self.shared.loop_i = 0
        self.shared.blink = None
        self.after(1, self.loop)

    def loop(self):
        if self.shared.loop_i % 10 == 0:
            if self.seedrandom['text'] == "Random":
                self.seedrandom.config(activeforeground=random_color())
            else:
                self.seedrandom.config(activeforeground='#faaffa')
        if getattr(self.shared, "prof_upd_required", False):
            self.update_profiler()
            self.shared.prof_upd_required = False
        self.after(50, self.loop)
        self.shared.loop_i += 1

    def post_init(self):
        self.seedinput.insert(0, "Hello, world!")
        self.update_seed()

    def update_and_execute(self, event=None):
        if getattr(self.shared, "proc", None):
            return
        self.update_seed(event)
        self.exec_btn_handler(event)

    def validate_seed(self, event=None):
        if self.seedinput.get().isnumeric():
            self.seedrandom.config(text="Random")
            self.shared.seed = int(self.seedinput.get())
        else:
            self.seedrandom.config(text="Update")

    def update_seed(self, event=None):
        if self.seedinput.get().isnumeric():
            self.shared.seed = random.randint(0, 0xffffffff)
        else:
            self.shared.seed = zlib.crc32(self.seedinput.get().encode('utf-8'))
        self.seedinput.delete(0, "end")
        self.seedinput.insert(0, str(self.shared.seed))
        self.validate_seed()

    def exec_btn_handler(self, event=None):
        if getattr(self.shared, "proc", None):
            self.shared.proc.kill()
            self.execblink("Killed.")
        else:
            self.execbutton.config(text="Preparing",
                                   fg="#ff0000",
                                   state="disabled")
            self.execute_code()

    def on_key_release(self, event):
        print(repr(event.keysym))

    def execute_code(self, event=None):
        if not getattr(self.shared, "src_image", None):
            self.execblink("No image", "#ffff00")
            self.status("No image given")
            return

        if event != "RUN":
            thr = Thread(target=self.execute_code, args=("RUN",))
            thr.start()
            return

        self.status("Starting...")
        self.profiler_canvas.delete("top-text")
        self.profiler_canvas.delete("pieslice")
        self.update()

        self.shared.profiler_info = {}
        code = self.codeblock._text.get('1.0', 'end')
        tempcode = tempfile.mkstemp('.py', 'detcher-')[1]
        with open(tempcode, 'w') as fd:
            fd.write(code)
        self.status("Preparing...")
        tempimg = tempfile.mkstemp('.png', 'detcher-')[1]
        self.shared.src_image.save(tempimg)

        self.execbutton.config(text="Kill",
                               fg="#ff0000",
                               state="normal")
        self.status("Running...")

        proc = Popen([
            sys.executable,
            "-u", "-B",
            sys.argv[0],
            "--IS-HELPER"
        ], stdin=PIPE, stdout=PIPE)

        self.shared.proc = proc
        proc.stdin.write(tempcode.encode() + b"\n")
        proc.stdin.write(tempimg.encode() + b"\n")
        proc.stdin.write(f"{self.shared.seed}\n".encode())
        proc.stdin.flush()

        err = [None, None]
        out, tmpdir = None, None
        line = b'-- -- --'

        while proc.poll() is None or len(line):
            line = proc.stdout.readline()
            if not line:
                continue
            if proc.poll():
                print("[INFO] Process finished but buffer is not empty")
            ln = line.decode().rstrip()
            if ln.startswith("\x1b"):
                cmd = ln.lstrip("\x1b")
                params = cmd.split(":")
                print(f">> {cmd}")
                name = params[0]
                if name == "OKDONE":
                    out = ":".join(params[1:])
                if name == "DR":
                    ok, name, cpu, real = params[1:]
                    cpu, real = map(float, [cpu, real])
                    self.after_call(name, [cpu, real])
                if name == "ERR":
                    err[0] = ":".join(params[1:])
                if name == "ERRF":
                    err[1] = ":".join(params[1:])
                if name == "ERR_NOTB":
                    err = [":".join(params[1:]), None]
                if name == "TMP":
                    tmpdir = ":".join(params[1:])
                if name == "DBG":
                    self.status(":".join(params[1:]), "#7878fa")
            else:
                print(f"[SUB][STDOUT]: {ln}")
                self.status(f"[sub] {ln.rstrip()}", "#7878fa")
        proc.wait()

        exitcode = proc.poll()
        print(f"[SUB] -> {exitcode}")

        self.shared.proc = None
        if exitcode:
            short_e, e_file = err
            trace = "-- no trace --"
            if e_file:
                with open(e_file, "r") as fd:
                    trace = fd.read()
                rm_file(e_file)
            self.execblink("Terminated" if exitcode <
                           0 else "Error", "#ff0000")
            self.status(f"{short_e or 'Terminated'}", "#ff0000")
            print(trace)
            self.shared.proc = None
            if tmpdir:
                shutil.rmtree(tmpdir)
            return

        self.status("Loading image...")
        self.shared.out_image = Image.open(out).copy()
        self.status("Cleaning files...")
        rm_file(tempcode)
        rm_file(tempimg)
        if tmpdir:
            shutil.rmtree(tmpdir)
        self.status("Updating...")
        self.update_image()
        self.execbutton.config(text="Execute", fg="#78fa78")
        self.status("Done.")

    def load_code_button_handler(self, event=None):
        filename = self.ask_file_read(CODE_FILE_TYPES)
        if not filename:
            print('no file')
            return
        try:
            with open(filename, "r") as f:
                code = f.read()
        except:
            print('read error', filename)
            return
        self.codeblock._text.delete('1.0', 'end')
        self.codeblock._text.insert('1.0', code)
        self.codeblock.redraw()

    def save_code_button_handler(self, event=None):
        filename = self.ask_file_write(CODE_FILE_TYPES)
        if not filename:
            return
        try:
            with open(filename, "w") as f:
                f.write(self.codeblock._text.get('1.0', 'end'))
        except Exception as e:
            print(e)

    def load_image_button_handler(self, event=None):
        filename = self.ask_file_read(IMAGE_FILE_TYPES)
        if not filename:
            return
        self.shared.src_image = Image.open(filename).convert("RGB")
        self.shared.out_image = self.shared.src_image
        self.update_image()

    def save_image_button_handler(self, event=None):
        filename = self.ask_file_write(IMAGE_FILE_TYPES)
        if not filename:
            return
        if not getattr(self.shared, 'out_image'):
            return
        self.shared.out_image.save(filename)

    def update_image(self):
        if not getattr(self.shared, 'out_image'):
            return
        canvassize = (
            self.imagepreview.winfo_reqwidth() - 2,
            self.imagepreview.winfo_reqheight() - 2
        )
        canvascenter = canvassize[0] // 2, canvassize[1] // 2
        self.shared._oimg_thumb = self.shared.out_image.copy()
        self.shared._oimg_thumb.thumbnail(canvassize)
        self.shared._tkimg = ImageTk.PhotoImage(self.shared._oimg_thumb)
        self.imagepreview.create_image(*canvascenter, image=self.shared._tkimg)
        image = self.shared.out_image
        image_dims = "Image dimensions: %dx%d" % image.size
        image_mode = f"Image mode: {image.mode}"
        dims_clr = get_status_color(40000, 2000000, image.width * image.height)
        print(dims_clr)
        self.profiler_canvas.itemconfig("image-dims",
                                        text=image_dims,
                                        fill=dims_clr)
        self.profiler_canvas.itemconfig("image-mode",
                                        text=image_mode)

    def show_image(self, event=None):
        if getattr(self.shared, 'out_image', None):
            self.shared.out_image.show()

    def execblink(self, text="-- message --", color="#ff0000"):
        self.execbutton.config(text=text, fg=color, state="normal")

        def delayed():
            self.execbutton.config(text="Execute", fg="#78fa78")
        self.after(500, delayed)

    def after_call(self, name, delta):
        value = self.shared.profiler_info.get(name, [0, 0, 0])
        value = [value[0] + delta[0], value[1] + delta[1], value[2] + 1]
        self.shared.profiler_info[name] = value
        self.shared.prof_upd_required = True

    def update_profiler(self):
        if not getattr(self.shared, "profiler_info", None):
            return

        profiler_info = dict(self.shared.profiler_info)
        totaltime = sum(map(lambda v: v[1], profiler_info.values()))
        pos = (10, 10, 110, 110)
        cur_angle = 0

        canvas = self.profiler_canvas

        for k, v in profiler_info.items():
            colorval = zlib.crc32(k.encode()) & 0x7f7f7f
            color = "#%.6x" % (colorval + 0x7f7f7f)
            angle = 360 * (v[1] / totaltime)
            if not canvas.find_withtag(f"pie-{k}"):
                canvas.create_arc(pos, tags=("pieslice", f"pie-{k}"),
                                  fill=color, outline=color)
            canvas.itemconfig(f"pie-{k}",
                              start=cur_angle,
                              extent=angle or 360)
            cur_angle += angle

        captures = list(profiler_info.items())
        most_longest = sorted(captures, key=lambda c: c[1][1], reverse=True)
        for i, (name, times) in zip(range(10), most_longest):
            if not canvas.find_withtag(f"text-{name}"):
                colorval = zlib.crc32(k.encode()) & 0x7f7f7f
                color = "#%.6x" % (colorval + 0x7f7f7f)
                canvas.create_text((110, 10 + (9 * i)),
                                   text="N/A",
                                   fill=color,
                                   font="monospace 8",
                                   anchor="nw",
                                   tags=("top-text", f"text-{name}"))
            top_str = f"{times[1] * 1000:4.0f}ms ({times[2]}) - {name}"
            canvas.itemconfig(f"text-{name}", text=top_str)
            canvas.coords(f"text-{name}", (120, 10 + (9 * i)))

        total_str = f"Total time: {totaltime * 1000:7.1f}ms"
        total_clr = get_status_color(0, 10, totaltime)
        canvas.itemconfig("total-time", text=total_str, fill=total_clr)
        canvas.update()

    def force_redraw_image(self, event=None):
        if getattr(self.shared, "_resized", False):
            self.update_image()
            self.shared._resized = False

    def status(self, text="--- --- --- --- ---", fg="#787878"):
        self.statusbar.config(text=text, fg=fg)
