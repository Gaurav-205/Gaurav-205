import json
import os
import sys
from datetime import datetime

def load_data(json_path="data/contributions.json"):
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run fetch_contributions.py first.")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_heatmap_svg(data, output_path="contrib-heatmap.svg", is_static=False):
    days = data["days"]
    total_contribs = data["total"]
    current_streak = data["current_streak"]
    longest_streak = data["longest_streak"]
    
    # 53 weeks x 7 days = 371 days
    # Chunk into weeks
    weeks = [days[i:i+7] for i in range(0, len(days), 7)]
    
    # SVG Grid spacing parameters
    width = 860
    height = 180
    
    left_padding = 40
    top_padding = 32
    box_size = 11.5
    gap = 3.5
    col_width = box_size + gap # 15px
    row_height = box_size + gap # 15px
    
    # Find month transitions for top headers
    month_labels = []
    prev_month = None
    for col_idx, week in enumerate(weeks):
        if not week:
            continue
        first_day_date = week[0]["date"]
        # Parse month name
        dt = datetime.strptime(first_day_date, "%Y-%m-%d")
        month_name = dt.strftime("%b")
        
        # Draw label if it's the first week of a month
        if month_name != prev_month:
            # Avoid labels too close to each other
            if not month_labels or (col_idx - month_labels[-1][0] >= 3):
                month_labels.append((col_idx, month_name))
                prev_month = month_name
                
    # Build animations stylesheet
    anim_style = ""
    if not is_static:
        anim_style = """
    @keyframes diagonalReveal {
      0% {
        opacity: 0;
        transform: translateY(-4px) scale(0.85);
      }
      100% {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }
    .box {
      opacity: 0;
      transform-origin: center;
      animation: diagonalReveal 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
"""
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('  <style>')
    svg.append('    .bg {')
    svg.append('      fill: transparent;')
    svg.append('    }')
    svg.append('    .label-month, .label-day, .legend-text, .footer-text {')
    svg.append('      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;')
    svg.append('      font-size: 10px;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .footer-text {')
    svg.append('      font-size: 11px;')
    svg.append('      fill: #8b949e;')
    svg.append('    }')
    svg.append('    .footer-text .highlight {')
    svg.append('      fill: #58a6ff;')
    svg.append('      font-weight: 600;')
    svg.append('    }')
    svg.append('    .legend-text {')
    svg.append('      font-size: 9px;')
    svg.append('    }')
    
    # Palette colors (Dark Mode defaults)
    svg.append('    .l-0 { fill: #161b22; }')
    svg.append('    .l-1 { fill: #0e4429; }')
    svg.append('    .l-2 { fill: #006d32; }')
    svg.append('    .l-3 { fill: #26a641; }')
    svg.append('    .l-4 { fill: #39d353; }')
    svg.append('    .l-5 { fill: #69f0a0; } /* Neon level for epic days */')
    
    # Light Mode override
    svg.append('    @media (prefers-color-scheme: light) {')
    svg.append('      .label-month, .label-day, .legend-text, .footer-text {')
    svg.append('        fill: #57606a;')
    svg.append('      }')
    svg.append('      .footer-text .highlight {')
    svg.append('        fill: #0969da;')
    svg.append('      }')
    svg.append('      .l-0 { fill: #ebedf0; }')
    svg.append('      .l-1 { fill: #9be9a8; }')
    svg.append('      .l-2 { fill: #40c463; }')
    svg.append('      .l-3 { fill: #30a14e; }')
    svg.append('      .l-4 { fill: #216e39; }')
    svg.append('      .l-5 { fill: #104a21; }')
    svg.append('    }')
    svg.append(anim_style)
    svg.append('  </style>')
    
    svg.append('  <rect class="bg" width="100%" height="100%" />')
    
    # Draw Month Labels
    svg.append('  <!-- Month Labels -->')
    for col_idx, name in month_labels:
        x_pos = left_padding + col_idx * col_width
        svg.append(f'  <text class="label-month" x="{x_pos}" y="20">{name}</text>')
        
    # Draw Day Labels (Mon, Wed, Fri)
    svg.append('  <!-- Day Labels -->')
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for r_idx, label in day_labels:
        y_pos = top_padding + r_idx * row_height + 9
        svg.append(f'  <text class="label-day" x="15" y="{y_pos}" text-anchor="start">{label}</text>')
        
    # Draw Contribution Grid
    svg.append('  <!-- Contribution Grid -->')
    for col_idx, week in enumerate(weeks):
        for row_idx, day in enumerate(week):
            date_str = day["date"]
            level = day["level"]
            count = day["count"]
            
            # Map count to l-5 class if it's high
            level_class = f"l-{level}"
            if count >= 10:
                level_class = "l-5"
                
            x_pos = left_padding + col_idx * col_width
            y_pos = top_padding + row_idx * row_height
            
            # Calculate staggered animation delay based on diagonal coordinates
            delay = (col_idx + row_idx) * 0.014
            
            anim_attr = ""
            if not is_static:
                anim_attr = f' class="box {level_class}" style="animation-delay: {delay:.3f}s;"'
            else:
                anim_attr = f' class="{level_class}"'
                
            tooltip_str = f"{count} contributions on {date_str}" if count != 1 else f"1 contribution on {date_str}"
            if count == 0:
                tooltip_str = f"No contributions on {date_str}"
                
            svg.append(f'  <rect x="{x_pos}" y="{y_pos}" width="{box_size}" height="{box_size}" rx="2" ry="2"{anim_attr}>')
            svg.append(f'    <title>{tooltip_str}</title>')
            svg.append(f'  </rect>')
            
    # Draw Footer (Total Contributions and Streak Info)
    svg.append('  <!-- Footer Stats -->')
    footer_y = top_padding + 7 * row_height + 26
    formatted_total = f"{total_contribs:,}"
    svg.append(f'  <text class="footer-text" x="{left_padding}" y="{footer_y}">')
    svg.append(f'    <tspan class="highlight">{formatted_total} contributions</tspan> in the last year')
    svg.append(f'    <tspan>  |  Current Streak: </tspan><tspan class="highlight">{current_streak} days</tspan>')
    svg.append(f'    <tspan>  |  Longest Streak: </tspan><tspan class="highlight">{longest_streak} days</tspan>')
    svg.append(f'  </text>')
    
    # Draw Legend (Less -> More)
    legend_x = width - 150
    legend_y = footer_y - 8
    svg.append('  <!-- Legend -->')
    svg.append(f'  <g class="legend" transform="translate({legend_x}, {legend_y})">')
    svg.append('    <text class="legend-text" x="0" y="9">Less</text>')
    
    # Draw legend squares
    legend_colors = ["l-0", "l-1", "l-2", "l-3", "l-4", "l-5"]
    for idx, l_color in enumerate(legend_colors):
        x_sq = 30 + idx * 13
        svg.append(f'    <rect class="{l_color}" x="{x_sq}" y="0" width="10" height="10" rx="1.5" ry="1.5" />')
        
    svg.append('    <text class="legend-text" x="112" y="9">More</text>')
    svg.append('  </g>')
    
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Heatmap SVG generated at {output_path} (Static: {is_static})")

if __name__ == "__main__":
    json_file = "data/contributions.json"
    output_file = "contrib-heatmap.svg"
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    static_mode = os.environ.get("STATIC") == "1"
    data = load_data(json_file)
    generate_heatmap_svg(data, output_file, static_mode)
