from PIL import Image, ImageDraw

def create_round_avatar(image, size=(80, 80)):
    """
    Создает круглый аватар из изображения
    """
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    
    image = image.resize(size, Image.LANCZOS)
    result = Image.new('RGBA', size)
    result.paste(image, (0, 0), mask)
    return result

def resize_image(image, max_width, max_height):
    """
    Изменяет размер изображения с сохранением пропорций
    """
    img = image.copy()
    img.thumbnail((max_width, max_height), Image.LANCZOS)
    return img

def create_default_avatar(size=(80, 80), color=(100, 150, 200)):
    """
    Создает аватар по умолчанию
    """
    avatar_img = Image.new('RGBA', size, color)
    draw = ImageDraw.Draw(avatar_img)
    draw.ellipse((0, 0, size[0], size[1]), fill=color)
    return avatar_img

def load_image_safe(image_path, default_size=(240, 160), default_color=(230, 247, 239)):
    """
    Безопасная загрузка изображения с fallback
    """
    try:
        return Image.open(image_path)
    except:
        return Image.new("RGBA", default_size, default_color)