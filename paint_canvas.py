"""
Core drawing mechanics for Pro Paint Studio.
Handles touch events, shape rendering, and state history (Undo/Redo).
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, InstructionGroup
from kivy.core.window import Window
from typing import List, Optional

class PaintCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brush_color: tuple = (1, 1, 1, 1)  # Default White
        self.brush_size: float = 5.0
        self.current_tool: str = 'brush' # Options: brush, eraser, line
        
        # History stacks for Undo/Redo functionality
        self.history: List[InstructionGroup] = []
        self.redo_stack: List[InstructionGroup] = []
        
        # Temporary storage for the current stroke being drawn
        self.current_stroke: Optional[InstructionGroup] = None
        self.current_line: Optional[Line] = None

    def on_touch_down(self, touch) -> bool:
        """Initializes a new drawing stroke when the screen is touched."""
        if not self.collide_point(touch.x, touch.y):
            return False

        with self.canvas:
            self.current_stroke = InstructionGroup()
            
            # Handle Eraser vs Brush colors
            if self.current_tool == 'eraser':
                color = Color(0.1, 0.1, 0.1, 1) # Matches background dark theme
            else:
                color = Color(*self.brush_color)
                
            self.current_line = Line(points=(touch.x, touch.y), width=self.brush_size)
            
            self.current_stroke.add(color)
            self.current_stroke.add(self.current_line)
            self.history.append(self.current_stroke)
            
            # Clear redo stack when a new action is taken
            self.redo_stack.clear()
            
        return True

    def on_touch_move(self, touch) -> bool:
        """Updates the current stroke as the user's finger moves."""
        if not self.collide_point(touch.x, touch.y) or not self.current_line:
            return False
            
        if self.current_tool in ['brush', 'eraser']:
            self.current_line.points += [touch.x, touch.y]
        elif self.current_tool == 'line':
            # For straight lines, update the end point rather than appending
            self.current_line.points = [self.current_line.points[0], self.current_line.points[1], touch.x, touch.y]
            
        return True

    def on_touch_up(self, touch) -> bool:
        """Finalizes the stroke."""
        self.current_stroke = None
        self.current_line = None
        return True

    def undo(self) -> None:
        """Removes the last stroke from the canvas and saves it to redo stack."""
        if self.history:
            last_stroke = self.history.pop()
            self.canvas.Here are the production-ready source files to construct the Pro Paint Studio project. These files follow professional Python conventions (PEP-8, Object-Oriented Design, type hinting, and modular UI structure) and are configured to compile automatically via GitHub Actions.

You need to create three specific files in your repository.

### 1. The Main Application Code (`main.py`)
This file contains the core Kivy application. It implements the drawing logic, undo/redo stacks via Kivy's `InstructionGroup`, and a responsive dark-themed UI.

```python
"""
Pro Paint Studio - Main Application Module
Provides a professional-grade drawing canvas with tools, undo/redo stacks, and file saving.
"""

import os
from typing import List, Optional

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, InstructionGroup, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex

# Set default clear color for professional dark mode UI
Window.clearcolor = get_color_from_hex('#1E1E1E')


class PaintCanvas(Widget):
    """Handles drawing operations, tool states, and the undo/redo history stack."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brush_color: List[float] = [1, 1, 1, 1]  # Default: White
        self.brush_size: float = 5.0
        self.current_tool: str = 'brush'
        
        # History stacks for Undo/Redo operations
        self.history: List[InstructionGroup] = []
        self.redo_stack: List[InstructionGroup] = []
        
        # Temporary references for current drawing action
        self.current_instruction: Optional[InstructionGroup] = None
        self.current_shape = None

    def on_touch_down(self, touch) -> bool:
        """Initializes a drawing instruction when the canvas is touched."""
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        self.current_instruction = InstructionGroup()
        self.current_instruction.add(Color(*self.brush_color))
        
        if self.current_tool == 'brush' or self.current_tool == 'line':
            self.current_shape = Line(points=(touch.x, touch.y), width=self.brush_size)
        elif self.current_tool == 'rect':
            self.current_shape = Rectangle(pos=(touch.x, touch.y), size=(0, 0))
        elif self.current_tool == 'circle':
            self.current_shape = Ellipse(pos=(touch.x, touch.y), size=(0, 0))
            
        self.current_instruction.add(self.current_shape)
        self.canvas.add(self.current_instruction)
        
        # Track origin for shapes
        touch.ud['start_pos'] = touch.pos
        return True

    def on_touch_move(self, touch) -> None:
        """Updates the current shape parameters as the user drags."""
        if not self.current_shape or not self.collide_point(*touch.pos):
            return

        if self.current_tool == 'brush':
            self.current_shape.points += [touch.x, touch.y]
        elif self.current_tool == 'line':
            start_x, start_y = touch.ud['start_pos']
            self.current_shape.points = [start_x, start_y, touch.x, touch.y]
        elif self.current_tool in ('rect', 'circle'):
            start_x, start_y = touch.ud['start_pos']
            width = touch.x - start_x
            height = touch.y - start_y
            self.current_shape.size = (width, height)

    def on_touch_up(self, touch) -> None:
        """Finalizes the drawing action and pushes it to the undo stack."""
        if self.current_instruction:
            self.history.append(self.current_instruction)
            self.redo_stack.clear()  # Clear redo on new action
            self.current_instruction = None
            self.current_shape = None

    def undo(self) -> None:
        """Reverts the last drawing action."""
        if not self.history:
            return
        last_action = self.history.pop()
        self.canvas.remove(last_action)
        self.redo_stack.append(last_action)

    def redo(self) -> None:
        """Restores the last undone action."""
        if not self.redo_stack:
            return
        restored_action = self.redo_stack.pop()
        self.canvas.add(restored_action)
        self.history.append(restored_action)

    def clear_canvas(self) -> None:
        """Wipes the canvas completely."""
        self.canvas.clear()
        self.history.clear()
        self.redo_stack.clear()

    def export_to_png(self, filename="pro_paint_export.png") -> None:
        """Exports the current canvas state to a PNG file."""
        self.export_to_png(filename)


class ProPaintUI(BoxLayout):
    """Main UI layout assembling the toolbar and the drawing canvas."""
    
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Canvas Area
        self.paint_canvas = PaintCanvas(size_hint=(1, 0.85))
        
        # Toolbar Area
        self.toolbar = BoxLayout(size_hint=(1, 0.15), padding=5, spacing=5)
        self._build_toolbar()
        
        self.add_widget(self.paint_canvas)
        self.add_widget(self.toolbar)

    def _build_toolbar(self) -> None:
        """Constructs the tools and controls for the bottom bar."""
        tools = [
            ('Brush', 'brush'), ('Line', 'line'), 
            ('Rect', 'rect'), ('Circle', 'circle')
        ]
        
        # Tool Buttons
        for text, mode in tools:
            btn = Button(text=text, background_color=(0.3, 0.3, 0.3, 1))
            btn.bind(on_release=lambda b, m=mode: self.set_tool(m))
            self.toolbar.add_widget(btn)

        # Actions
        undo_btn = Button(text='Undo', on_release=lambda x: self.paint_canvas.undo())
        redo_btn = Button(text='Redo', on_release=lambda x: self.paint_canvas.redo())
        color_btn = Button(text='Color', on_release=self.show_color_picker)
        
        # Size Slider
        self.size_slider = Slider(min=1, max=80, value=5)
        self.size_slider.bind(value=self.update_brush_size)

        for widget in (undo_btn, redo_btn, color_btn, self.size_slider):
            self.toolbar.add_widget(widget)

    def set_tool(self, mode: str) -> None:
        self.paint_canvas.current_tool = mode

    def update_brush_size(self, instance, value: float) -> None:
        self.paint_canvas.brush_size = value

    def show_color_picker(self, instance) -> None:
        picker = ColorPicker()
        popup = Popup(title="Select Color", content=picker, size_hint=(0.9, 0.9))
        picker.bind(color=self._on_color_selection)
        popup.open()

    def _on_color_selection(self, instance, value: List[float]) -> None:
        self.paint_canvas.brush_color = value


class ProPaintApp(App):
    def build(self) -> ProPaintUI:
        self.title = "Pro Paint Studio"
        return ProPaintUI()


if __name__ == '__main__':
    ProPaintApp().run()
