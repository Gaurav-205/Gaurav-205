import math
import random
from PIL import Image, ImageDraw

def create_stargazing_gif(output_path="stargazing.gif", width=800, height=500, num_frames=60):
    # Set seed for reproducible star positions and shooting stars
    random.seed(42)
    
    # 1. Generate stars with random positions, sizes, phases, and speeds
    stars = []
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, int(height * 0.85)) # Keep stars above the hill
        max_r = random.uniform(0.6, 2.2)
        phase = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.08, 0.18)
        stars.append({'x': x, 'y': y, 'max_r': max_r, 'phase': phase, 'speed': speed})
        
    # 2. Define shooting stars
    # We will trigger two shooting stars in the loop
    shooting_stars = [
        {
            'start_frame': 10,
            'duration': 12,
            'start_pos': (200, 40),
            'end_pos': (450, 140),
            'color': (230, 240, 255)
        },
        {
            'start_frame': 35,
            'duration': 12,
            'start_pos': (700, 60),
            'end_pos': (500, 180),
            'color': (220, 235, 255)
        }
    ]
    
    frames = []
    
    for f in range(num_frames):
        # Create base frame with vertical sky gradient
        # From deep midnight blue (#02020a) to a slightly lighter night blue (#0b0c25)
        base = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(base)
        
        # Draw sky gradient
        r1, g1, b1 = 2, 2, 10
        r2, g2, b2 = 12, 14, 40
        for y in range(height):
            ratio = y / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
            
        # Draw twinkling stars
        for star in stars:
            # Twinkle formula
            intensity = 0.25 + 0.75 * abs(math.sin(f * star['speed'] + star['phase']))
            r = star['max_r'] * intensity
            
            x, y = star['x'], star['y']
            if r > 1.2:
                # Draw a nice soft glowing star
                draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=(245, 248, 255))
                # Add a tiny horizontal/vertical glow cross for larger stars
                if star['max_r'] > 1.8 and intensity > 0.8:
                    draw.line([(x - 3, y), (x + 3, y)], fill=(255, 255, 255, 150))
                    draw.line([(x, y - 3), (x, y + 3)], fill=(255, 255, 255, 150))
            else:
                # Just draw a single pixel star
                gray_val = int(100 + 155 * intensity)
                draw.point((x, y), fill=(gray_val, gray_val, int(gray_val * 1.1)))
                
        # Draw active shooting stars
        for ss in shooting_stars:
            sf = ss['start_frame']
            dur = ss['duration']
            if sf <= f < sf + dur:
                t = (f - sf) / dur
                start_x, start_y = ss['start_pos']
                end_x, end_y = ss['end_pos']
                
                # Current head position
                head_x = start_x + (end_x - start_x) * t
                head_y = start_y + (end_y - start_y) * t
                
                # Draw tail (fading back to start)
                # Tail length increases and then fades
                tail_t = max(0.0, t - 0.4)
                tail_x = start_x + (end_x - start_x) * tail_t
                tail_y = start_y + (end_y - start_y) * tail_t
                
                # Draw main streak line
                draw.line([(tail_x, tail_y), (head_x, head_y)], fill=ss['color'], width=2)
                # Draw glowing head
                draw.ellipse([(head_x - 2, head_y - 2), (head_x + 2, head_y + 2)], fill=(255, 255, 255))
                
        # Draw silhouette hill at the bottom
        # A smooth dark curve (#030308)
        draw.chord([(-150, 360), (width + 150, 580)], 180, 360, fill=(3, 3, 8))
        
        # Draw tree silhouette on the left side
        # Tree trunk
        draw.polygon([(60, 480), (80, 480), (85, 220), (55, 220)], fill=(2, 2, 6))
        # Branches
        draw.line([(70, 240), (25, 150)], fill=(2, 2, 6), width=8)
        draw.line([(70, 220), (140, 130)], fill=(2, 2, 6), width=8)
        draw.line([(35, 168), (10, 120)], fill=(2, 2, 6), width=5)
        draw.line([(120, 152), (170, 100)], fill=(2, 2, 6), width=5)
        
        # Foliage clusters (overlapping dark circles)
        foliage_color = (1, 1, 4)
        draw.ellipse([(5, 80), (85, 160)], fill=foliage_color)
        draw.ellipse([(95, 70), (185, 150)], fill=foliage_color)
        draw.ellipse([(50, 60), (140, 140)], fill=foliage_color)
        draw.ellipse([(-20, 100), (60, 180)], fill=foliage_color)
        draw.ellipse([(140, 80), (210, 145)], fill=foliage_color)
        
        # Draw stargazing person silhouette sitting on the hill
        px, py = 360, 378
        # Head
        draw.ellipse([(px - 6, py - 24), (px + 6, py - 12)], fill=(2, 2, 5))
        # Torso (angled slightly backward looking up)
        draw.polygon([(px - 4, py - 12), (px + 4, py - 12), (px + 6, py + 12), (px - 6, py + 12)], fill=(2, 2, 5))
        # Bent Legs
        draw.line([(px - 2, py + 12), (px + 16, py + 4)], fill=(2, 2, 5), width=6)
        draw.line([(px + 16, py + 4), (px + 22, py + 18)], fill=(2, 2, 5), width=5)
        # Arms resting on knees
        draw.line([(px + 2, py - 6), (px + 14, py + 5)], fill=(2, 2, 5), width=4)
        
        # Draw a small telescope silhouette pointing up to the sky
        tx, ty = px + 35, py + 4
        # Tripod stand lines
        draw.line([(tx, ty), (tx - 10, ty + 16)], fill=(1, 1, 3), width=2)
        draw.line([(tx, ty), (tx + 10, ty + 16)], fill=(1, 1, 3), width=2)
        # Telescope tube pointing diagonally up-right (~30 degrees)
        draw.line([(tx - 12, ty + 6), (tx + 20, ty - 12)], fill=(2, 2, 6), width=5)
        
        frames.append(base)
        
    # Save the frames as an animated GIF
    # 60ms per frame gives a smooth 16.6 FPS animation
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=70,
        loop=0
    )
    print(f"Stargazing GIF created at {output_path} ({width}x{height}, {num_frames} frames)")

if __name__ == "__main__":
    create_stargazing_gif()
