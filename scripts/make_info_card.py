import os
import sys

def generate_info_card(output_path="info-card.svg", is_static=False):
    # Retrieve user options/env if needed, but we hardcode gorgeous defaults
    username = "Gaurav-205"
    hostname = "github"
    
    # Neofetch details
    details = [
        ("OS", "Windows Server / Windows 11"),
        ("Host", "GitHub Profile (Gaurav-205)"),
        ("Kernel", "Node.js, Next.js, Flutter"),
        ("Uptime", "3 shipped products, 457 users"),
        ("Shell", "PowerShell / Git Bash"),
        ("Stack", "TypeScript, React, Flutter, Node, Firebase, SQL"),
        ("Now", "Building scalable MERN, Next.js, and AI systems"),
        ("Projects", "KampusKart, Nova Career, Onam Event Platform"),
        ("Highlights", "10k+ AI emails, INR 48K+ sales, 58 endpoints")
    ]
    
    # SVG size parameters
    width = 490
    height = 360
    
    # CSS animations setup
    anim_style = ""
    anim_attrs = {}
    if not is_static:
        # Generate inline keyframes and staggered delays
        anim_style = """
    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    .anim-fade {
      animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
"""
        for i in range(len(details) + 4): # Details + header elements
            anim_style += f"    .delay-{i} {{ animation-delay: {0.1 + i * 0.08:.2f}s; }}\n"
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('  <style>')
    svg.append('    .window-bg {')
    svg.append('      fill: #0d1117; /* Dark theme default */')
    svg.append('      stroke: #30363d;')
    svg.append('      stroke-width: 1.5;')
    svg.append('    }')
    svg.append('    .title-text {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;')
    svg.append('      font-size: 13px;')
    svg.append('      fill: #8b949e;')
    svg.append('      text-anchor: middle;')
    svg.append('    }')
    svg.append('    .term-text {')
    svg.append('      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;')
    svg.append('      font-size: 12px;')
    svg.append('      line-height: 1.5;')
    svg.append('    }')
    svg.append('    .header-user {')
    svg.append('      fill: #58a6ff; /* blue */')
    svg.append('      font-weight: bold;')
    svg.append('    }')
    svg.append('    .header-host {')
    svg.append('      fill: #58a6ff;')
    svg.append('    }')
    svg.append('    .header-at {')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .separator {')
    svg.append('      fill: #21262d;')
    svg.append('    }')
    svg.append('    .key-color {')
    svg.append('      fill: #58a6ff;')
    svg.append('      font-weight: bold;')
    svg.append('    }')
    svg.append('    .val-color {')
    svg.append('      fill: #c9d1d9;')
    svg.append('    }')
    svg.append('    /* Color blocks */')
    svg.append('    .c-black { fill: #161b22; }')
    svg.append('    .c-red { fill: #f85149; }')
    svg.append('    .c-green { fill: #39d353; }')
    svg.append('    .c-yellow { fill: #f2cc60; }')
    svg.append('    .c-blue { fill: #58a6ff; }')
    svg.append('    .c-magenta { fill: #bc8cff; }')
    svg.append('    .c-cyan { fill: #39c5cf; }')
    svg.append('    .c-white { fill: #ffffff; stroke: #30363d; stroke-width: 0.5; }')
    
    # Light theme overrides
    svg.append('    @media (prefers-color-scheme: light) {')
    svg.append('      .window-bg {')
    svg.append('        fill: #ffffff;')
    svg.append('        stroke: #d0d7de;')
    svg.append('      }')
    svg.append('      .title-text {')
    svg.append('        fill: #57606a;')
    svg.append('      }')
    svg.append('      .header-user {')
    svg.append('        fill: #0969da; /* dark blue */')
    svg.append('      }')
    svg.append('      .header-host {')
    svg.append('        fill: #0969da;')
    svg.append('      }')
    svg.append('      .header-at {')
    svg.append('        fill: #57606a;')
    svg.append('      }')
    svg.append('      .separator {')
    svg.append('        fill: #d0d7de;')
    svg.append('      }')
    svg.append('      .key-color {')
    svg.append('        fill: #0969da;')
    svg.append('      }')
    svg.append('      .val-color {')
    svg.append('        fill: #24292f;')
    svg.append('      }')
    svg.append('      .c-black { fill: #f6f8fa; }')
    svg.append('      .c-red { fill: #cf222e; }')
    svg.append('      .c-green { fill: #1a7f37; }')
    svg.append('      .c-yellow { fill: #9a6700; }')
    svg.append('      .c-blue { fill: #0969da; }')
    svg.append('      .c-magenta { fill: #8250df; }')
    svg.append('      .c-cyan { fill: #1f6feb; }')
    svg.append('      .c-white { fill: #24292f; stroke: none; }')
    svg.append('    }')
    svg.append(anim_style)
    svg.append('  </style>')
    
    # Background terminal window
    svg.append('  <!-- Terminal Frame -->')
    svg.append(f'  <rect class="window-bg" x="1.5" y="1.5" width="{width - 3}" height="{height - 3}" rx="8" ry="8" />')
    
    # Terminal Title Bar and Buttons
    svg.append('  <!-- Terminal Header -->')
    svg.append('  <circle cx="20" cy="20" r="5.5" fill="#ff5f56" />')
    svg.append('  <circle cx="36" cy="20" r="5.5" fill="#ffbd2e" />')
    svg.append('  <circle cx="52" cy="20" r="5.5" fill="#27c93f" />')
    svg.append(f'  <text class="title-text" x="{width // 2}" y="24">{username}@{hostname}</text>')
    
    # Details offset and vertical flow
    start_y = 58
    line_gap = 21
    
    anim_class = "anim-fade" if not is_static else ""
    
    # Header: user@host
    svg.append(f'  <!-- Neofetch content -->')
    svg.append(f'  <g class="{anim_class} delay-0 term-text">')
    svg.append(f'    <text x="20" y="{start_y}">')
    svg.append(f'      <tspan class="header-user">{username}</tspan>')
    svg.append(f'      <tspan class="header-at">@</tspan>')
    svg.append(f'      <tspan class="header-host">{hostname}</tspan>')
    svg.append(f'    </text>')
    svg.append(f'  </g>')
    
    # Separator row
    svg.append(f'  <g class="{anim_class} delay-1 term-text">')
    # Use a solid dashed line for neofetch style
    separator_line = "-" * (len(username) + len(hostname) + 1)
    svg.append(f'    <text x="20" y="{start_y + 10}" class="separator">{separator_line}</text>')
    svg.append(f'  </g>')
    
    # Render key-value pairs
    y_offset = start_y + 26
    for idx, (key, value) in enumerate(details):
        delay_class = f"delay-{idx + 2}" if not is_static else ""
        
        # Split value if it is too long for the card width
        # 490px width fits roughly 45 characters of 12px monospace text
        max_chars = 40
        if len(value) > max_chars:
            # Split nicely on spaces
            words = value.split(" ")
            lines = []
            current_line = []
            for word in words:
                if len(" ".join(current_line + [word])) <= max_chars:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
        else:
            lines = [value]
            
        svg.append(f'  <g class="{anim_class} {delay_class} term-text">')
        svg.append(f'    <text x="20" y="{y_offset}">')
        svg.append(f'      <tspan class="key-color">{key}</tspan>')
        svg.append(f'      <tspan class="val-color">: {lines[0]}</tspan>')
        svg.append(f'    </text>')
        
        # If there are additional lines, indent them
        for sub_line in lines[1:]:
            y_offset += 15
            svg.append(f'    <text x="20" y="{y_offset}">')
            indent = " " * (len(key) + 2)
            svg.append(f'      <tspan class="val-color">{indent}{sub_line}</tspan>')
            svg.append(f'    </text>')
            
        svg.append(f'  </g>')
        y_offset += line_gap
        
    # Render colored blocks at the bottom
    color_y = y_offset + 5
    blocks_delay = f"delay-{len(details) + 2}" if not is_static else ""
    svg.append(f'  <!-- ANSI Color Blocks -->')
    svg.append(f'  <g class="{anim_class} {blocks_delay}">')
    
    colors = ["c-black", "c-red", "c-green", "c-yellow", "c-blue", "c-magenta", "c-cyan", "c-white"]
    block_width = 18
    block_height = 14
    spacing = 6
    
    for i, c_class in enumerate(colors):
        x_pos = 20 + i * (block_width + spacing)
        svg.append(f'    <rect class="{c_class}" x="{x_pos}" y="{color_y}" width="{block_width}" height="{block_height}" rx="2" />')
        
    svg.append('  </g>')
    
    svg.append('</svg>')
    
    # Write SVG
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Info card SVG generated at {output_path} (Static: {is_static})")

if __name__ == "__main__":
    output_file = "info-card.svg"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        
    # Check if STATIC=1 env variable is set
    static_mode = os.environ.get("STATIC") == "1"
    generate_info_card(output_file, static_mode)
