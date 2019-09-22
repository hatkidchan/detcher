import re
geom_regex = re.compile(r"(\d+)x(\d+)\+([\d\-]+)\+([\d\-]+)")


class AdaptiveMixIn:
    def get_geometry(self):
        geometry = geom_regex.findall(self.geometry())[0]
        width, height, top, left = map(int, geometry)
        return width, height, top, left

    def on_resize(self, event=None):
        width, height, top, left = self.get_geometry()

        if width < 800 or height < 500:
            width, height = max([width, 800]), max([height, 500])
            self.geometry(f"{width}x{height}+{top}+{left}")
            self.update()
            self._reorder_widgets()
            return

        if not getattr(self, "_geom", None):
            self._geom = (width, height)
        if self._geom == (width, height):
            return
        self._reorder_widgets()
        self.shared._resized = True

    def _reorder_widgets(self):
        for name, widget in self._widgets_list.items():
            widget.place_forget()
        self._place_widgets()
