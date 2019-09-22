import time
import random
import numpy as np
import traceback
from PIL import ImageColor

class Timer(object):
    def __init__(self):
        self.start_time = None
        self.start_cpu_time = None
        self.cpu = -1
        self.real = -1

    def start(self):
        self.start_time = time.time()
        self.start_cpu_time = time.process_time()

    def stop(self):
        cpudelta = time.process_time() - self.start_cpu_time
        timedelta = time.time() - self.start_time
        self.cpu = cpudelta
        self.real = timedelta


class WrappedFunction(object):
    def __init__(self, function, master):
        self._function = function
        self._master = master
        self.name = self._function.__name__

    def __call__(self, *args, **kwargs):
        try:
            timer = Timer()
            timer.start()
            value = self._function(*args, **kwargs)
            timer.stop()
        except Exception as e:
            timer.stop()
            tbs = traceback.format_exc()
            self._master.after_call_cb(False, self.name, [e, tbs], [timer.cpu, timer.real])
            raise e
        else:
            self._master.after_call_cb(True, self.name, value, [timer.cpu, timer.real])
            return value


class TimeMonitor(object):
    def __init__(self):
        self.funcs = []
        self.after_call_cb = lambda *a: None

    def after_call(self, func):
        self.after_call_cb = func
        return func

    def __call__(self, func):
        wrapped = WrappedFunction(func, self)
        self.funcs.append(wrapped)
        return wrapped


def random_color():
    return '#%.6x' % random.randint(0, 0xffffff)

def get_status_color(minv, maxv, curv, saturation=50, lightness=100):
    percents = (curv - minv) / (maxv - minv)
    value = min(1.0, max(0.0, percents))
    hsvcolor = f"hsv({270 - value * 270}, {saturation}%, {lightness}%)"
    return "#%.2x%.2x%.2x"%ImageColor.getrgb(hsvcolor)