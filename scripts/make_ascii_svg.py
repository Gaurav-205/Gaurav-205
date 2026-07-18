import sys
import os
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # Bright (white background) to dark (dense foreground)

def image_to_ascii(image_path, width=80):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        sys.exit(1)
        
    img = Image.open(image_path)
    img_w, img_h = img.size
    
    # Calculate height based on aspect ratio and typical character aspect ratio (~0.55)
    char_aspect = 0.55
    aspect_ratio = img_h / img_w
    height = int(width * aspect_ratio * char_aspect)
    
    # Resize image to target grid size
    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Ensure it is grayscale
    if resized_img.mode != "L":
        resized_img = resized_img.convert("L")
        
    pixels = resized_img.load()
    
    ascii_rows = []
    for y in range(height):
        row = ""
        for x in range(width):
            pixel_val = pixels[x, y]
            # Map 255 (white) to 0 (space), 0 (black) to RAMP last index (dense glyph)
            ramp_idx = int((255 - pixel_val) / 255 * (len(RAMP) - 1))
            ramp_idx = max(0, min(len(RAMP) - 1, ramp_idx))
            row += RAMP[ramp_idx]
        ascii_rows.append(row)
        
    return ascii_rows

def escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def generate_svg(ascii_rows, output_path="avi-ascii.svg"):
    grid_height = len(ascii_rows)
    grid_width = len(ascii_rows[0]) if grid_height > 0 else 0
    
    char_width = 7.2
    char_height = 13.0
    padding_x = 10
    padding_y = 15
    
    svg_width = int(grid_width * char_width + padding_x * 2)
    svg_height = int(grid_height * char_height + padding_y * 2)
    
    # Animation settings
    total_typing_time = 2.2 # Total seconds for the typing effect
    row_dur = 0.25 # Duration to type a single row
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%">')
    
    # Styles supporting responsive GitHub light/dark themes
    svg.append('  <style>')
    svg.append('    text {')
    svg.append('      fill: #24292f; /* Light mode default */')
    svg.append('      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;')
    svg.append('      font-size: 11px;')
    svg.append('      font-weight: 500;')
    svg.append('    }')
    svg.append('    .cursor {')
    svg.append('      fill: #0969da; /* Sleek accent color for cursor (e.g. blue) */')
    svg.append('    }')
    svg.append('    @media (prefers-color-scheme: dark) {')
    svg.append('      text {')
    svg.append('        fill: #c9d1d9; /* Dark mode text */')
    svg.append('      }')
    svg.append('      .cursor {')
    svg.append('        fill: #58a6ff; /* Dark mode cursor color */')
    svg.append('      }')
    svg.append('    }')
    svg.append('  </style>')
    
    # Clip paths for row-by-row typing
    svg.append('  <defs>')
    for i, row in enumerate(ascii_rows):
        # Trim trailing spaces to find actual text end for cursor and clip length
        r_trimmed = row.rstrip()
        row_len = len(r_trimmed)
        if row_len == 0:
            row_len = 1
            
        row_y = padding_y + i * char_height
        delay = (i / grid_height) * total_typing_time
        
        svg.append(f'    <clipPath id="clip-row-{i}">')
        svg.append(f'      <rect x="{padding_x}" y="{row_y}" width="0" height="{char_height}">')
        svg.append(f'        <animate attributeName="width" from="0" to="{row_len * char_width}" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" />')
        svg.append(f'      </rect>')
        svg.append(f'    </clipPath>')
    svg.append('  </defs>')
    
    # Background - let's make it transparent to blend with GitHub
    svg.append('  <!-- Text Rows and Cursors -->')
    for i, row in enumerate(ascii_rows):
        r_trimmed = row.rstrip()
        row_len = len(r_trimmed)
        row_y = padding_y + i * char_height
        text_y = row_y + char_height - 2.5 # baseline adjustment
        delay = (i / grid_height) * total_typing_time
        
        escaped_text = escape_xml(row)
        
        # Render text with clip path
        svg.append(f'  <text x="{padding_x}" y="{text_y}" xml:space="preserve" clip-path="url(#clip-row-{i})">{escaped_text}</text>')
        
        # Render moving block cursor for this row
        if row_len > 0:
            svg.append(f'  <rect x="{padding_x}" y="{row_y + 1}" width="{char_width}" height="{char_height - 2}" class="cursor" opacity="0">')
            svg.append(f'    <animate attributeName="x" from="{padding_x}" to="{padding_x + row_len * char_width}" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" />')
            svg.append(f'    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.92;1" dur="{row_dur}s" begin="{delay:.3f}s" fill="freeze" />')
            svg.append(f'  </rect>')
            
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"ASCII SVG generated at {output_path} with {grid_width}x{grid_height} grid.")

if __name__ == "__main__":
    input_img = "source-prepped.png"
    output_svg = "gaurav-ascii.svg"
    
    if len(sys.argv) > 1:
        input_img = sys.argv[1]
    if len(sys.argv) > 2:
        output_svg = sys.argv[2]
        
    # Standard width of 85 characters gives a clean layout
    rows = image_to_ascii(input_img, width=85)
    generate_svg(rows, output_svg)
