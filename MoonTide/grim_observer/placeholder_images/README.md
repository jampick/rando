# Discord Embed Placeholder Images

These are placeholder images generated for testing Discord embeds in `grim_observer.py`.

## 📁 Generated Images

### Core Images (Default)
- **`thumbnail.png`** (96x96) - 💀 Skull icon for general use
- **`main_image.png`** (400x300) - "CROM SLEEPS" message for empty servers
- **`footer_icon.png`** (16x16) - ⚔️ Sword icon for footer

### Map-Specific Images
- **`thumbnail_siptah.png`** (96x96) - 🌴 Palm tree + "SIPTAH" for Siptah map
- **`thumbnail_exiled.png`** (96x96) - 🏔️ Mountain + "EXILED" for Exiled map
- **`main_image_siptah.png`** (400x300) - "THE DARKNESS FALLS" theme for Siptah
- **`main_image_exiled.png`** (400x300) - "SILENCE REIGNS" theme for Exiled

## 🚀 How to Use

### Option 1: Upload to Image Hosting Service
1. **Upload** these images to an image hosting service:
   - [Imgur](https://imgur.com/) (recommended)
   - [Discord](https://discord.com/) (upload to your server)
   - [GitHub](https://github.com/) (in your repository)
   - Your own web server

2. **Use the URLs** in your grim_observer.py command:
   ```bash
   python grim_observer.py monitor log.txt --map siptah \
     --thumbnail-url "https://your-domain.com/thumb.png" \
     --main-image-url "https://your-domain.com/main.png" \
     --footer-icon-url "https://your-domain.com/icon.png"
   ```

### Option 2: Update Default URLs in Code
Edit `grim_observer.py` and update the default image URLs:
```python
self.empty_server_images = {
    'thumbnail': 'https://your-domain.com/thumb.png',
    'main_image': 'https://your-domain.com/main.png',
    'footer_icon': 'https://your-domain.com/icon.png'
}
```

### Option 3: Use Map-Specific Images
For different maps, you can use the themed images:
- **Siptah**: Use `thumbnail_siptah.png` and `main_image_siptah.png`
- **Exiled**: Use `thumbnail_exiled.png` and `main_image_exiled.png`

## 🎨 Image Specifications

- **Thumbnail**: 96x96px (small icon, top-right of embed)
- **Main Image**: 400x300px max (large image below embed)
- **Footer Icon**: 16x16px (small icon next to footer text)
- **Format**: PNG (transparent background support)
- **Colors**: Themed to match CROM aesthetic

## 🔄 Regenerating Images

If you want to create new placeholder images:

### On Mac/Linux:
```bash
chmod +x generate_placeholders.sh
./generate_placeholders.sh
```

### On Windows:
```bash
generate_placeholders.bat
```

### Manual Python:
```bash
# Install Pillow first
pip install Pillow

# Run the script
python placeholder_images.py
```

## 💡 Customization Ideas

- **Change colors**: Edit the color values in `placeholder_images.py`
- **Add text**: Modify the text strings for different themes
- **Change fonts**: Update font paths for different system fonts
- **Add logos**: Replace text with your server logo or branding

## ⚠️ Important Notes

- **HTTPS Required**: Discord only accepts HTTPS image URLs
- **Public Access**: Images must be publicly accessible
- **File Size**: Keep images under 8MB for Discord
- **Dimensions**: Stick to recommended sizes for best display

## 🎯 Next Steps

1. **Upload** your chosen images to a hosting service
2. **Test** the URLs in Discord to ensure they work
3. **Configure** grim_observer.py with your image URLs
4. **Enjoy** your epic CROM-themed empty server messages! ⚔️💀
