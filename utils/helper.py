import os
import tempfile
import traceback
import sys
from .glitcher import exports, mon, Image


def communicate(*args, **kwargs):
    sys.stdout.write(args[0])
    sys.stdout.write("\n")
    sys.stdout.flush()


def main(args):
    communicate(f"\x1bDBG:Process started")
    tmpd = tempfile.mkdtemp("-tmp", "dtchr-")

    communicate(f"\x1bTMP:{tmpd}")

    @mon.after_call
    def mon_cb(ok, name, v, times):
        if ok:
            communicate(f"\x1bDR:1:{name}:{times[0]}:{times[1]}")
        else:
            communicate(f"\x1bDR:0:{name}:{times[0]}:{times[1]}")
            communicate(f"\x1bERR:{v[0]!s}")
            traceback_path = os.path.join(tmpd, "traceback.txt")
            with open(traceback_path, "w") as fd:
                fd.write(v[1])
            communicate(f"\x1bERRF:{traceback_path}")
            quit(3)

    code_filename = input()
    input_image = input()
    seed = int(input())

    communicate(f"\x1bDBG:Loading image...")

    try:
        image = Image.open(input_image)
        image = image.convert("RGB")
    except Exception as e:
        communicate(f"\x1bERR_NOTB:{e!s}")
        quit(1)

    try:
        with open(code_filename, "r") as fd:
            code = fd.read()
    except Exception as e:
        communicate(f"\x1bERR_NOTB:{e!s}")
        quit(2)

    namespace = dict(exports)
    namespace['np'].random.seed(seed)
    namespace['random'].seed(seed)
    namespace.update({
        'image': image,
        'seed': seed,
        'rand': namespace['np'].random.uniform,
        'randint': namespace['np'].random.randint,
        '__file__': __file__,
        '__name__': __name__
    })

    communicate(f"\x1bDBG:Executing...")
    try:
        exec(code, namespace)
    except Exception as e:
        communicate(f"\x1bERR:{e!s}")
        traceback_path = os.path.join(tmpd, "traceback.txt")
        with open(traceback_path, "w") as fd:
            fd.write(traceback.format_exc())
        communicate(f"\x1bERRF:{traceback_path}")
        quit(4)

    communicate(f"\x1bDBG:Saving image...")

    im = namespace["image"]
    out_path = os.path.join(tmpd, "output.png")
    im.save(out_path)
    communicate(f"\x1bOKDONE:{out_path}")
