#!/usr/bin/env python3
"""
Generate placeholder icons for the browser extension
"""

from PIL import Image, ImageDraw
import os

ICON_SIZES = [16, 48, 128]
ICON_DIR = os.path.join(os.path.dirname(__file__), '..', 'extension', 'icons')
BRAND_COLOR = '#4A90E2'

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_icon(size: int, output_path: str):
    """Create a simple circular icon with checkmark"""
    # Create new image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate dimensions
    padding = size // 8
    circle_size = size - (2 * padding)

    # Draw circle
    color = hex_to_rgb(BRAND_COLOR)
    draw.ellipse(
        [padding, padding, padding + circle_size, padding + circle_size],
        fill=color,
        outline=None
    )

    # Draw checkmark (simple version)
    checkmark_color = (255, 255, 255)
    line_width = max(2, size // 16)

    # Short vertical line
    x1 = size // 3
    y1 = size // 2
    x2 = size // 2 - size // 16
    y2 = size * 2 // 3
    draw.line([x1, y1, x2, y2], fill=checkmark_color, width=line_width)

    # Long diagonal line
    x3 = size * 2 // 3
    y3 = size // 3
    draw.line([x2, y2, x3, y3], fill=checkmark_color, width=line_width)

    # Save
    img.save(output_path, 'PNG')
    print(f'✓ Created {os.path.basename(output_path)} ({size}x{size})')

def main():
    # Ensure icons directory exists
    os.makedirs(ICON_DIR, exist_ok=True)

    print('Generating extension icons...')

    for size in ICON_SIZES:
        output_path = os.path.join(ICON_DIR, f'icon{size}.png')
        create_icon(size, output_path)

    # Also copy to dist if it exists
    dist_icon_dir = os.path.join(os.path.dirname(__file__), '..', 'extension', 'dist', 'icons')
    if os.path.exists(os.path.dirname(dist_icon_dir)):
        os.makedirs(dist_icon_dir, exist_ok=True)
        for size in ICON_SIZES:
            src = os.path.join(ICON_DIR, f'icon{size}.png')
            dst = os.path.join(dist_icon_dir, f'icon{size}.png')
            if os.path.exists(src):
                import shutil
                shutil.copy(src, dst)
                print(f'✓ Copied to dist/icons/icon{size}.png')

    print('\n✅ All icons generated successfully!')
    print(f'📁 Location: {ICON_DIR}')

if __name__ == '__main__':
    main()
