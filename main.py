"""Kivy Paint Pro

Features
--------
* Tools: Brush, Eraser, Line, Rectangle, Ellipse (with optional Fill)
* Unlimited undo / redo (including undo of "Clear")
* Quick colour palette + full colour picker
* Brush size and opacity sliders
* Save drawing as PNG (white background included)
* Keyboard shortcuts: Ctrl+Z undo, Ctrl+Y / Ctrl+Shift+Z redo,
  Ctrl+S save, Delete clear
"""

import os
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, InstructionGroup, Line, Rectangle
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

BG_COLOR = (1, 1, 1, 1)
PALETTE = [
    (0, 0, 0), (1, 1, 1), (0.9, 0.1, 0.1), (1, 0.55, 0.0),
    (1, 0.9, 0.1), (0.15, 0.7, 0.25), (0.1, 0.5, 0.95), (0.55, 0.2, 0.8),
]


class DrawingWidget(Widget):
    tool = StringProperty('brush')          # brush, eraser, line, rect, ellipse
    line_color = ListProperty([0, 0, 0])
    line_width = NumericProperty(5)
    opacity_value = NumericProperty(1.0)
    fill = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []       # (kind, groups) entries for undo
        self.visible = []       # groups currently on the canvas
        self.redo_stack = []
        with self.canvas.before:
            Color(*BG_COLOR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    # ---------- helpers ----------
    def _clamp(self, x, y):
        return (min(max(x, self.x), self.right), min(max(y, self.y), self.top))

    def _rect_args(self, x0, y0, x1, y1):
        return (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))

    # ---------- touch ----------
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        x, y = self._clamp(*touch.pos)
        w = self.line_width
        group = InstructionGroup()

        if self.tool == 'eraser':
            group.add(Color(*BG_COLOR))
            w *= 2
        else:
            group.add(Color(*self.line_color, self.opacity_value))

        shape = None
        if self.tool in ('brush', 'eraser'):
            group.add(Ellipse(pos=(x - w / 2, y - w / 2), size=(w, w)))  # dot on tap
            shape = Line(points=[x, y], width=w / 2, cap='round', joint='round')
            group.add(shape)
        elif self.tool == 'line':
            shape = Line(points=[x, y, x, y], width=w / 2, cap='round')
            group.add(shape)
        elif self.tool == 'rect':
            shape = Rectangle(pos=(x, y), size=(0, 0)) if self.fill else \
                Line(rectangle=(x, y, 0, 0), width=w / 2)
            group.add(shape)
        elif self.tool == 'ellipse':
            shape = Ellipse(pos=(x, y), size=(0, 0)) if self.fill else \
                Line(ellipse=(x, y, 0, 0), width=w / 2)
            group.add(shape)

        self.canvas.add(group)
        touch.ud.update(owner=self, group=group, shape=shape,
                        start=(x, y), tool=self.tool, fill=self.fill)
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.ud.get('owner') is not self:
            return super().on_touch_move(touch)

        x, y = self._clamp(*touch.pos)
        x0, y0 = touch.ud['start']
        shape, tool = touch.ud['shape'], touch.ud['tool']

        if tool in ('brush', 'eraser'):
            shape.points += [x, y]
        elif tool == 'line':
            shape.points = [x0, y0, x, y]
        elif tool == 'rect':
            rx, ry, rw, rh = self._rect_args(x0, y0, x, y)
            if touch.ud['fill']:
                shape.pos, shape.size = (rx, ry), (rw, rh)
            else:
                shape.rectangle = (rx, ry, rw, rh)
        elif tool == 'ellipse':
            rx, ry, rw, rh = self._rect_args(x0, y0, x, y)
            if touch.ud['fill']:
                shape.pos, shape.size = (rx, ry), (rw, rh)
            else:
                shape.ellipse = (rx, ry, rw, rh)
        return True

    def on_touch_up(self, touch):
        if touch.ud.get('owner') is not self:
            return super().on_touch_up(touch)
        touch.ungrab(self)
        self.visible.append(touch.ud['group'])
        self.history.append(('add', [touch.ud['group']]))
        self.redo_stack.clear()
        return True

    # ---------- actions ----------
    # history entries are (kind, groups): kind is 'add' or 'clear'
    def _apply(self, kind, groups, forward):
        adding = (kind == 'add') == forward
        for g in groups:
            if adding:
                self.canvas.add(g)
                self.visible.append(g)
            else:
                self.canvas.remove(g)
                self.visible.remove(g)

    def undo(self):
        if self.history:
            kind, groups = self.history.pop()
            self._apply(kind, groups, forward=False)
            self.redo_stack.append((kind, groups))

    def redo(self):
        if self.redo_stack:
            kind, groups = self.redo_stack.pop()
            self._apply(kind, groups, forward=True)
            self.history.append((kind, groups))

    def clear(self):
        if not self.visible:
            return
        groups = list(self.visible)
        self._apply('clear', groups, forward=True)
        self.history.append(('clear', groups))
        self.redo_stack.clear()

    def save_png(self):
        folder = os.getcwd()
        name = datetime.now().strftime('paint_%Y%m%d_%H%M%S.png')
        path = os.path.join(folder, name)
        self.export_to_png(path)
        return path


class ColorPickerPopup(Popup):
    def __init__(self, callback, current_color, **kwargs):
        super().__init__(title='Pick a colour', size_hint=(0.9, 0.9), **kwargs)
        self.callback = callback
        content = BoxLayout(orientation='vertical', padding=10, spacing=8)
        self.color_picker = ColorPicker(color=current_color)
        content.add_widget(self.color_picker)
        btn = Button(text='Select Colour', size_hint=(1, 0.12))
        btn.bind(on_release=self._select)
        content.add_widget(btn)
        self.content = content

    def _select(self, *args):
        self.callback(self.color_picker.color)
        self.dismiss()


class PaintApp(App):
    title = 'Kivy Paint Pro'

    def build(self):
        root = BoxLayout(orientation='vertical')

        # ---- tool row ----
        tools = BoxLayout(size_hint=(1, None), height=48)
        for label, key in [('Brush', 'brush'), ('Eraser', 'eraser'), ('Line', 'line'),
                           ('Rect', 'rect'), ('Oval', 'ellipse')]:
            tb = ToggleButton(text=label, group='tool', allow_no_selection=False,
                              state='down' if key == 'brush' else 'normal')
            tb.bind(on_press=lambda inst, k=key: self.set_tool(k))
            tools.add_widget(tb)
        self.fill_btn = ToggleButton(text='Fill')
        self.fill_btn.bind(state=lambda i, v: setattr(self.canvas_widget, 'fill', v == 'down'))
        tools.add_widget(self.fill_btn)
        root.add_widget(tools)

        # ---- canvas ----
        self.canvas_widget = DrawingWidget()
        root.add_widget(self.canvas_widget)

        # ---- palette row ----
        palette = BoxLayout(size_hint=(1, None), height=40)
        for c in PALETTE:
            b = Button(background_normal='', background_color=(*c, 1))
            b.bind(on_release=lambda inst, col=c: self.set_color(col))
            palette.add_widget(b)
        self.color_button = Button(text='More', size_hint_x=1.5)
        self.color_button.bind(on_release=self.show_color_picker)
        palette.add_widget(self.color_button)
        root.add_widget(palette)

        # ---- sliders row ----
        sliders = BoxLayout(size_hint=(1, None), height=44)
        sliders.add_widget(Label(text='Size', size_hint_x=0.25))
        size_slider = Slider(min=1, max=40, value=5)
        size_slider.bind(value=lambda i, v: setattr(self.canvas_widget, 'line_width', v))
        sliders.add_widget(size_slider)
        sliders.add_widget(Label(text='Opacity', size_hint_x=0.3))
        op_slider = Slider(min=0.05, max=1, value=1)
        op_slider.bind(value=lambda i, v: setattr(self.canvas_widget, 'opacity_value', v))
        sliders.add_widget(op_slider)
        root.add_widget(sliders)

        # ---- action row ----
        actions = BoxLayout(size_hint=(1, None), height=48)
        for text, fn in [('Undo', self.undo), ('Redo', self.redo),
                         ('Clear', self.clear), ('Save PNG', self.save)]:
            b = Button(text=text)
            b.bind(on_release=lambda inst, f=fn: f())
            actions.add_widget(b)
        root.add_widget(actions)

        Window.bind(on_keyboard=self.on_key)
        return root

    # ---------- handlers ----------
    def set_tool(self, tool):
        self.canvas_widget.tool = tool

    def set_color(self, color):
        self.canvas_widget.line_color = list(color[:3])
        self.color_button.background_color = (*color[:3], 1)
        self.color_button.background_normal = ''
        if self.canvas_widget.tool == 'eraser':
            self.canvas_widget.tool = 'brush'

    def show_color_picker(self, *args):
        ColorPickerPopup(self.set_color, [*self.canvas_widget.line_color, 1]).open()

    def undo(self):
        self.canvas_widget.undo()

    def redo(self):
        self.canvas_widget.redo()

    def clear(self):
        self.canvas_widget.clear()

    def save(self):
        path = self.canvas_widget.save_png()
        self.toast(f'Saved to\n{path}')

    def toast(self, message):
        popup = Popup(title='', separator_height=0, size_hint=(0.8, 0.25),
                      content=Label(text=message, halign='center'))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def on_key(self, window, key, scancode, codepoint, modifiers):
        if 'ctrl' in modifiers:
            if codepoint == 'z' and 'shift' in modifiers:
                self.redo()
            elif codepoint == 'z':
                self.undo()
            elif codepoint == 'y':
                self.redo()
            elif codepoint == 's':
                self.save()
            else:
                return False
            return True
        if key == 127:  # Delete
            self.clear()
            return True
        return False


if __name__ == '__main__':
    PaintApp().run()
