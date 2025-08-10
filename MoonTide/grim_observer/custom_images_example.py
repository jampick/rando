#!/usr/bin/env python3
"""
Custom Images Configuration Example for Grim Observer

This file shows you exactly how to customize your Discord embed images.
Copy this file, update the URLs with your custom images, and use it as a reference.

🎯 QUICK START:
1. Upload your images to Imgur, Discord, or your own server
2. Replace the example URLs below with your actual image URLs
3. Copy the updated configuration to grim_observer.py
4. Restart Grim Observer

⚠️  REQUIREMENTS:
- Images must be publicly accessible via HTTPS
- PNG format recommended (transparent background support)
- Thumbnail: 96x96px, Main Image: 400x300px max, Footer Icon: 16x16px
- File size under 8MB for Discord compatibility
"""

# ============================================================================
# 🖼️  YOUR CUSTOM IMAGE URLs - REPLACE THESE WITH YOUR ACTUAL IMAGES
# ============================================================================

# Option 1: Simple replacement (recommended for most users)
CUSTOM_IMAGE_URLS = {
    "thumbnail": "https://your-domain.com/your-server-logo.png",
    "main_image": "https://your-domain.com/your-server-banner.png", 
    "footer_icon": "https://your-domain.com/your-footer-icon.png"
}

# Option 2: Map-specific customization (advanced users)
MAP_SPECIFIC_IMAGES = {
    "thumbnail": {
        "default": "https://your-domain.com/your-default-logo.png",
        "exiled": "https://your-domain.com/your-exiled-logo.png",
        "siptah": "https://your-domain.com/your-siptah-logo.png"
    },
    "main_image": {
        "default": "https://your-domain.com/your-default-banner.png",
        "exiled": "https://your-domain.com/your-exiled-banner.png",
        "siptah": "https://your-domain.com/your-siptah-banner.png"
    },
    "footer_icon": "https://your-domain.com/your-footer-icon.png"
}

# Option 3: Multiple image options for randomization
MULTIPLE_IMAGE_OPTIONS = {
    "thumbnail": [
        "https://your-domain.com/your-logo-1.png",
        "https://your-domain.com/your-logo-2.png",
        "https://your-domain.com/your-logo-3.png"
    ],
    "main_image": [
        "https://your-domain.com/your-banner-1.png",
        "https://your-domain.com/your-banner-2.png",
        "https://your-domain.com/your-banner-3.png"
    ],
    "footer_icon": [
        "https://your-domain.com/your-icon-1.png",
        "https://your-domain.com/your-icon-2.png"
    ]
}

# ============================================================================
# 🔧  HOW TO USE THESE CONFIGURATIONS
# ============================================================================

def show_usage_examples():
    """Show examples of how to use these configurations."""
    
    print("🎯 HOW TO USE YOUR CUSTOM IMAGES:")
    print("=" * 50)
    
    print("\n1️⃣  SIMPLE REPLACEMENT (Option 1):")
    print("   - Replace the URLs in grim_observer.py")
    print("   - Use the CUSTOM_IMAGE_URLS structure above")
    print("   - Restart Grim Observer")
    
    print("\n2️⃣  MAP-SPECIFIC CUSTOMIZATION (Option 2):")
    print("   - Different images for different maps")
    print("   - Use the MAP_SPECIFIC_IMAGES structure above")
    print("   - Requires code modification")
    
    print("\n3️⃣  MULTIPLE IMAGES FOR RANDOMIZATION (Option 3):")
    print("   - Multiple image options per type")
    print("   - Images randomly selected each time")
    print("   - Use the MULTIPLE_IMAGE_OPTIONS structure above")
    
    print("\n4️⃣  COMMAND-LINE OVERRIDE:")
    print("   - Use --thumbnail-url, --main-image-url, --footer-icon-url")
    print("   - Overrides default configuration")
    print("   - Good for testing different images")

def show_image_requirements():
    """Show image requirements and recommendations."""
    
    print("\n📋 IMAGE REQUIREMENTS:")
    print("=" * 30)
    
    print("✅ Format: PNG (transparent background support)")
    print("✅ Dimensions:")
    print("   - Thumbnail: 96x96px")
    print("   - Main Image: 400x300px max")
    print("   - Footer Icon: 16x16px")
    print("✅ Access: Must be publicly accessible via HTTPS")
    print("✅ Size: Under 8MB for Discord compatibility")
    
    print("\n🎨 RECOMMENDATIONS:")
    print("=" * 25)
    print("• Use high-quality images with transparent backgrounds")
    print("• Keep file sizes reasonable (under 1MB if possible)")
    print("• Test images in Discord before deploying")
    print("• Consider map-specific themes for immersion")
    print("• Use consistent branding across all images")

def show_hosting_options():
    """Show image hosting options."""
    
    print("\n🌐 IMAGE HOSTING OPTIONS:")
    print("=" * 30)
    
    print("1️⃣  Imgur (Recommended):")
    print("   - Free, reliable, HTTPS by default")
    print("   - Easy to use, good for testing")
    print("   - URL format: https://i.imgur.com/IMAGE_ID.png")
    
    print("\n2️⃣  Discord:")
    print("   - Upload to your Discord server")
    print("   - Right-click → Copy Link")
    print("   - URL format: https://cdn.discordapp.com/attachments/...")
    
    print("\n3️⃣  Your Own Server:")
    print("   - Full control over images")
    print("   - Must have HTTPS certificate")
    print("   - URL format: https://your-domain.com/images/...")
    
    print("\n4️⃣  GitHub:")
    print("   - Upload to your repository")
    print("   - Use raw.githubusercontent.com URLs")
    print("   - Good for version-controlled images")

def show_code_integration():
    """Show how to integrate with grim_observer.py."""
    
    print("\n💻 CODE INTEGRATION:")
    print("=" * 25)
    
    print("1️⃣  Find this section in grim_observer.py (around line 270):")
    print("   self.empty_server_image_options = {")
    print("       'thumbnail': [...],")
    print("       'main_image': [...],")
    print("       'footer_icon': [...]")
    print("   }")
    
    print("\n2️⃣  Replace the placeholder URLs with your custom URLs:")
    print("   'thumbnail': [")
    print("       'https://your-domain.com/your-logo.png'")
    print("   ],")
    
    print("\n3️⃣  Save the file and restart Grim Observer")
    print("   Your custom images will now be used automatically!")

if __name__ == "__main__":
    print("🎨 GRIM OBSERVER CUSTOM IMAGES GUIDE")
    print("=" * 40)
    
    show_usage_examples()
    show_image_requirements()
    show_hosting_options()
    show_code_integration()
    
    print("\n🚀 NEXT STEPS:")
    print("=" * 15)
    print("1. Upload your images to a hosting service")
    print("2. Update the URLs in this file with your actual image URLs")
    print("3. Copy the configuration to grim_observer.py")
    print("4. Test your custom images")
    print("5. Enjoy your branded Discord embeds! 🎉")
