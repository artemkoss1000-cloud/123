# main.py — 3D куб на Kivy с ручной 3D-проекцией
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Line, Color
from kivy.clock import Clock
import math


def project_3d_to_2d(x, y, z, cx, cy, scale=1.0, camera_z=5.0):
    """Проекция 3D точки на 2D экран."""
    factor = camera_z / (camera_z + z)
    px = cx + x * factor * scale
    py = cy + y * factor * scale
    return px, py


def rotate_point(x, y, z, rx, ry, rz):
    """Вращение точки вокруг трёх осей."""
    cx_, sx_ = math.cos(math.radians(rx)), math.sin(math.radians(rx))
    y, z = y * cx_ - z * sx_, y * sx_ + z * cx_
    cy_, sy_ = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    x, z = x * cy_ + z * sy_, -x * sy_ + z * cy_
    cz_, sz_ = math.cos(math.radians(rz)), math.sin(math.radians(rz))
    x, y = x * cz_ - y * sz_, x * sz_ + y * cz_
    return x, y, z


class CubeWidget(Widget):
    VERTICES = [
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
    ]
    EDGES = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rx = 20
        self.ry = 30
        self.rz = 0
        self.touch_last = None
        self.is_touching = False
        self.bind(size=self.redraw, pos=self.redraw)
        Clock.schedule_interval(self.auto_rotate, 1 / 60.0)

    def auto_rotate(self, dt):
        if not self.is_touching:
            self.ry += 0.5
            self.rx += 0.15
            self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        cx = self.width / 2
        cy = self.height / 2
        scale = min(self.width, self.height) * 0.18
        projected = []
        for vx, vy, vz in self.VERTICES:
            x, y, z = rotate_point(vx, vy, vz, self.rx, self.ry, self.rz)
            px, py = project_3d_to_2d(x, y, z, cx, cy, scale)
            projected.append((px, py, z))
        with self.canvas:
            for i, j in self.EDGES:
                x1, y1, _ = projected[i]
                x2, y2, _ = projected[j]
                z_avg = (projected[i][2] + projected[j][2]) / 2.0
                k = max(0.2, min(1.0, (z_avg + 2) / 4.0))
                Color(0.2 * k, 0.7 * k, 1.0, 1.0)
                Line(points=[x1, y1, x2, y2], width=2)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_last = touch.pos
            self.is_touching = True
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_touching and self.touch_last:
            dx = touch.x - self.touch_last[0]
            dy = touch.y - self.touch_last[1]
            self.ry += dx * 0.5
            self.rx += dy * 0.5
            self.touch_last = touch.pos
            self.redraw()
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.is_touching:
            self.is_touching = False
            self.touch_last = None
            return True
        return super().on_touch_up(touch)


class CubeApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        self.cube = CubeWidget()
        root.add_widget(self.cube)
        btn = Button(text='Сбросить вращение', size_hint=(1, 0.15), font_size='16sp')
        btn.bind(on_press=self.reset_rotation)
        root.add_widget(btn)
        return root

    def reset_rotation(self, *args):
        self.cube.rx = 20
        self.cube.ry = 30
        self.cube.rz = 0
        self.cube.redraw()


if __name__ == '__main__':
    CubeApp().run()