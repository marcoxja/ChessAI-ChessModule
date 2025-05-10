import pygame as pg
import sys



def darken_color(hex_color, factor=0.9):
    """Darkens a given hex color by a factor (default: 80% of original brightness)."""
    color = pg.Color(hex_color)  # ✅ Create a Pygame color object
    r, g, b = color.r, color.g, color.b  # ✅ Extract RGB values only

    # Apply darkening factor
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    
    return (r, g, b)  # ✅ Return the corrected RGB tuple

class Button:
    def __init__(self, text_or_image, width, height, pos, screen, font_or_image, elevation, primary_color, font_color):
        # Core attributes
        self.pressed = False
        self.hovered = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = pos[1]

        # Top rectangle
        self.top_rect = pg.Rect(pos, (width, height))  # Positioned based on the top-left corner of the button
        self.top_color = pg.Color(primary_color)  # Primary color of the button

        # Bottom rectangle
        self.bottom_rect = pg.Rect(pos, (width, elevation))
        self.bottom_color = darken_color(primary_color, factor=0.6)  # Darker shade for the bottom rectangle

        # Handle text or image
        if text_or_image is None:
            self.surf = font_or_image
            self.text_rect = self.surf.get_rect(center=self.top_rect.center)
        else:
            self.surf = font_or_image.render(text_or_image, True, font_color)  # Render the text
            self.text_rect = self.surf.get_rect(center=self.top_rect.center)

    def draw(self, screen):
        # Elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        # Draw the button
        pg.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius=12)
        pg.draw.rect(screen, self.top_color, self.top_rect, border_radius=12)  # Border radius for rounded corners
        screen.blit(self.surf, self.text_rect)

    def check_click(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]

        # Check if the mouse is hovering over the button
        if self.top_rect.collidepoint(mouse_pos):
            self.hovered = True
            self.top_color = '#D74B4B'  # Change color on hover
            if mouse_pressed:
                self.dynamic_elevation = 0
                if not self.pressed:
                    self.pressed = True
                    return True  # Button was clicked
            else:
                self.dynamic_elevation = self.elevation
                self.pressed = False
        else:
            self.hovered = False
            self.dynamic_elevation = self.elevation
            self.top_color = pg.Color('#555555')  # Reset to default color

        return False

                
        