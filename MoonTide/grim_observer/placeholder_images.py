#!/usr/bin/env python3
"""
Generate placeholder images for Discord embeds in grim_observer.py
This script creates simple placeholder images that can be used for testing.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(width, height, text, filename, bg_color=(50, 50, 50), text_color=(255, 255, 255)):
    """Create a placeholder image with text."""
    # Create image with background
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        # Try to use a system font
        font_size = min(width, height) // 8
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save image
    img.save(filename)
    print(f"Created: {filename} ({width}x{height})")
    return filename

def main():
    """Generate all placeholder images."""
    # Create images directory if it doesn't exist
    os.makedirs("placeholder_images", exist_ok=True)
    
    # Generate placeholder images
    images = [
        # Thumbnail (96x96) - Small icon
        (96, 96, "💀", "placeholder_images/thumbnail.png", (139, 0, 0), (255, 255, 255)),
        
        # Main image (400x300) - Large empty server image
        (400, 300, "CROM\nSLEEPS\n\nSERVER\nEMPTY", "placeholder_images/main_image.png", (25, 25, 25), (255, 215, 0)),
        
        # Footer icon (16x16) - Small footer icon
        (16, 16, "⚔️", "placeholder_images/footer_icon.png", (0, 0, 0), (255, 255, 255)),
        
        # Alternative thumbnail for Siptah (96x96)
        (96, 96, "🌴\nSIPTAH", "placeholder_images/thumbnail_siptah.png", (34, 139, 34), (255, 255, 255)),
        
        # Alternative thumbnail for Exiled (96x96)
        (96, 96, "🏔️\nEXILED", "placeholder_images/thumbnail_exiled.png", (139, 69, 19), (255, 255, 255)),
        
        # Alternative main image for Siptah (400x300)
        (400, 300, "THE DARKNESS\nFALLS\n\nSIPTAH\nEMPTY", "placeholder_images/main_image_siptah.png", (25, 50, 25), (144, 238, 144)),
        
        # Alternative main image for Exiled (400x300)
        (400, 300, "SILENCE\nREIGNS\n\nEXILED\nEMPTY", "placeholder_images/main_image_exiled.png", (50, 25, 25), (255, 228, 196))
    ]
    
    print("Generating placeholder images for Discord embeds...")
    print("=" * 50)
    
    for img_data in images:
        create_placeholder_image(*img_data)
    
    print("=" * 50)
    print("All placeholder images created!")
    print("\nUsage:")
    print("1. Upload these images to an image hosting service (Imgur, Discord, etc.)")
    print("2. Use the URLs in your grim_observer.py configuration:")
    print("   --thumbnail-url 'https://your-domain.com/thumb.png'")
    print("   --main-image-url 'https://your-domain.com/main.png'")
    print("   --footer-icon-url 'https://your-domain.com/icon.png'")
    print("\nOr update the default URLs in grim_observer.py:")
    print("   self.empty_server_images = {")
    print("       'thumbnail': 'your-thumbnail-url',")
    print("       'main_image': 'your-main-image-url',")
    print("       'footer_icon': 'your-footer-icon-url'")
    print("   }")

if __name__ == "__main__":
    main()
