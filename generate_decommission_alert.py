from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

def generate_decommission_gif(background_path="images/alertimage.png", output_path="docs/decommission_alert.gif"):
    end_date = datetime(2025, 12, 31)
    today = datetime.now()
    frames = []
    # new_size = (1600, 800)  # Increased height for larger text
    new_size=(1200,600)
    # Scale font size based on image dimensions for better adaptability
    font_size = int(min(new_size) * 0.35)  # 35% of smaller dimension for larger text

    # Try to load a bold font
    try:
        base_font = ImageFont.truetype("arialbd.ttf", font_size)
    except IOError:
        base_font = ImageFont.load_default()

    # Open the input GIF and get all frames
    bg_gif = Image.open(background_path)
    bg_frames = []
    try:
        while True:
            bg_frames.append(bg_gif.copy())
            bg_gif.seek(len(bg_frames))  # Move to next frame
    except EOFError:
        pass  # End of sequence

    num_bg_frames = len(bg_frames)

    total_frames = 10  # Number of frames in the GIF
    for i in range(total_frames):
        # Each frame is one second apart
        target = end_date - (today + timedelta(seconds=i))
        days = target.days
        text = f"{days} days left for decommissioning Current-Gen!"

        bg = bg_frames[i % num_bg_frames].convert("RGBA")
        bg = bg.resize(new_size, Image.LANCZOS)
        width, height = bg.size

        overlay = Image.new("RGBA", bg.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Dynamically adjust font size to fit with better scaling
        temp_font_size = font_size
        min_font_size = int(min(width, height) * 0.05)  # Minimum 5% of smaller dimension
        while True:
            try:
                font = ImageFont.truetype("arialbd.ttf", temp_font_size)
            except IOError:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if text_width < width * 0.90 and text_height < height * 0.50:  # Allow more reasonable space
                break
            temp_font_size -= max(1, temp_font_size // 15)  # Reduce by smaller increments
            if temp_font_size < min_font_size:
                temp_font_size = min_font_size
                break

        x = (width - text_width) // 2

        # Animation: Slide up and fade in
        # Start lower and move up, fade in alpha
        start_y = height - int(height * 0.15)
        end_y = height - text_height - int(height * 0.08)
        y = int(start_y - (start_y - end_y) * (i / (total_frames - 1)))
        alpha = int(255 * (i + 1) / total_frames)  # Fade in

        # Draw semi-transparent rounded rectangle behind text
        rect_margin_x = int(text_width * 0.15)
        rect_margin_y = int(text_height * 0.25)
        rect_x0 = x - rect_margin_x
        rect_y0 = y - rect_margin_y
        rect_x1 = x + text_width + rect_margin_x
        rect_y1 = y + text_height + rect_margin_y
        rect_radius = int(min(rect_margin_x, rect_margin_y, 30))
        rect_color = (0, 0, 0, int(180 * (i + 1) / total_frames))  # Animate alpha

        try:
            draw.rounded_rectangle([rect_x0, rect_y0, rect_x1, rect_y1], radius=rect_radius, fill=rect_color)
        except AttributeError:
            draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=rect_color)

        # Draw shadow with size-appropriate offset
        shadow_offset = max(2, int(min(width, height) * 0.003))  # Scale shadow with image size
        shadow_color = (0, 0, 0, int(200 * (i + 1) / total_frames))
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)

        # Draw main text (red, animated alpha)
        draw.text((x, y), text, fill=(255, 0, 0, alpha), font=font)

        # Composite overlay onto background and add to frames
        frame = Image.alpha_composite(bg, overlay).convert("P")
        frames.append(frame)

    # Save all frames as a GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=500,
        loop=0
    )

def generate_static_image(size, output_path, background_path="images/alertimage.png"):
    from datetime import datetime
    from PIL import Image, ImageDraw, ImageFont

    end_date = datetime(2025, 12, 31)
    today = datetime.now()
    days = (end_date - today).days
    text = f"{days} Days Left!"

    width, height = size
    # Improved font selection and sizing based on image dimensions
    # Increase font size for better visibility in the bottom banner
    base_font_size = int(min(width, height) * 0.35)  # 35% of smaller dimension for larger text
    
    # Use DejaVuSans-Bold font for all images for consistent sizing
    try:
        from PIL import ImageFont
        font_path = ImageFont.truetype("DejaVuSans-Bold.ttf", 10).path
    except Exception:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Common Linux path
    # If not found, fallback to PIL's default font

    # Prepare background and overlay
    bg = Image.open(background_path).convert("RGBA")
    bg = bg.resize(size, Image.LANCZOS)
    overlay = Image.new("RGBA", bg.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Calculate banner height before font sizing
    banner_height = int(height * 0.13)

    # Dynamically adjust font size to fill the bottom banner as much as possible
    temp_font_size = int(banner_height * 1.1)  # Start with 110% of banner height
    min_font_size = int(banner_height * 0.80)    # Minimum 80% of banner height
    while True:
        try:
            font = ImageFont.truetype(font_path, temp_font_size)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        # Fit within 99% width and 98% banner height
        if text_width < width * 0.99 and text_height < banner_height * 0.98:
            break
        temp_font_size -= max(1, temp_font_size // 10)
        if temp_font_size < min_font_size:
            temp_font_size = min_font_size
            break


    # Draw a bottom banner for the "days left" text
    banner_height = int(height * 0.13)
    banner_y0 = height - banner_height
    banner_y1 = height
    banner_color = (0, 0, 0, 180)  # Semi-transparent black
    draw.rectangle([0, banner_y0, width, banner_y1], fill=banner_color)

    # Center the text vertically in the banner
    bottom_text = text
    bottom_font = font
    bottom_bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
    bottom_text_width = bottom_bbox[2] - bottom_bbox[0]
    bottom_text_height = bottom_bbox[3] - bottom_bbox[1]
    bottom_x = (width - bottom_text_width) // 2
    bottom_y = banner_y0 + (banner_height - bottom_text_height) // 2

    # Draw shadow for bottom text with size-appropriate offset
    shadow_offset = max(2, int(min(width, height) * 0.003))  # Scale shadow with image size
    draw.text((bottom_x + shadow_offset, bottom_y + shadow_offset), bottom_text, font=bottom_font, fill=(0, 0, 0, 255))
    # Draw main bottom text (white)
    draw.text((bottom_x, bottom_y), bottom_text, fill=(255, 255, 255, 255), font=bottom_font)

    # Add generated date/time label at the top center with appropriate sizing
    generated_label = f"Generated: {today.strftime('%Y-%m-%d %H:%M:%S')}"
    # Scale label font size appropriately (5-8% of smaller dimension)
    label_font_size = max(16, int(min(width, height) * 0.06))  # Minimum 16px, max 6% of smaller dimension  
    try:
        label_font = ImageFont.truetype("arial.ttf", label_font_size)
    except IOError:
        label_font = ImageFont.load_default()
    label_bbox = draw.textbbox((0, 0), generated_label, font=label_font)
    label_width = label_bbox[2] - label_bbox[0]
    label_height = label_bbox[3] - label_bbox[1]
    label_x = (width - label_width) // 2
    label_y = 10  # Top margin

    # Draw a semi-transparent rectangle behind the label for readability
    label_rect_color = (0, 0, 0, 120)
    draw.rectangle(
        [label_x - 5, label_y - 2, label_x + label_width + 5, label_y + label_height + 2],
        fill=label_rect_color
    )
    # Draw the label text (white)
    draw.text((label_x, label_y), generated_label, fill=(255, 255, 255, 255), font=label_font)

    result = Image.alpha_composite(bg, overlay).convert("RGB")
    result.save(output_path)

if __name__ == "__main__":
    generate_decommission_gif()
    print("Decommission alert GIF generated successfully.")

    # Generate static images in various sizes
    sizes = {
       # "small": (640, 480),        # Standard small (VGA) (640, 480)
       # "medium": (1280, 720),      # HD (1280, 720)
       # "large": (1920, 1080),      # Full HD (1920, 1080)
       # "banner": (1200, 400)       # Typical web banner (1200, 400) 
        "small": (320, 240),        # QVGA standard (320, 240)
        "medium": (640, 480),       # VGA standard (640, 480)
        "large": (800, 580),        # SVGA standard (800, 600)
        "banner": (1200, 500)
    }
    for name, size in sizes.items():
        output_path = f"docs/decommission_alert_{name}.jpg"
        generate_static_image(size, output_path)
        print(f"Static {name} image generated at {output_path}")