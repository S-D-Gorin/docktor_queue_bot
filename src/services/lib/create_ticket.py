from PIL import Image, ImageDraw, ImageFont
import os

def create_ticket(data, template_config, template_path, output_path):
    """
    Продвинутая версия с центрированием текста и поддержкой кириллицы.
    """
    
    # Конфигурация полей с примерными координатами
    fields_config = {
        "hospital_name": {
            "coords": (int(template_config["hospital_name"]["coords_x"]), int(template_config["hospital_name"]["coords_y"])),  # Координаты (x, y)
            "font_size": int(template_config["hospital_name"]["font_size"]),  # Размер шрифта
            "color": (0, 0, 0),  # Черный цвет
            "max_width": 400  # Максимальная ширина текста
        },
        "full_name": {
            "coords": (int(template_config["full_name"]["coords_x"]), int(template_config["full_name"]["coords_y"])),
            "font_size": int(template_config["full_name"]["font_size"]),
            "color": (0, 0, 0),
            "max_width": 400
        },
        "datetime": {
            "coords": (int(template_config["datetime"]["coords_x"]), int(template_config["datetime"]["coords_y"])),
            "font_size": int(template_config["datetime"]["font_size"]),
            "color": (0, 0, 0),
            "max_width": 300
        },
        "docktor_type": {
            "coords": (int(template_config["docktor_type"]["coords_x"]), int(template_config["docktor_type"]["coords_y"])),
            "font_size": int(template_config["docktor_type"]["font_size"]),
            "color": (0, 0, 0),
            "max_width": 300
        },
        "docktor_name": {
            "coords": (int(template_config["docktor_name"]["coords_x"]), int(template_config["docktor_name"]["coords_y"])),
            "font_size": int(template_config["docktor_name"]["font_size"]),
            "color": (0, 0, 0),
            "max_width": 300
        }
    }
    
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Используйте шрифт с поддержкой кириллицы
    try:
        # Попробуйте разные шрифты
        font_paths = [
            "arial.ttf",
            "/app/app_files/fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in font_paths:
            try:
                base_font = ImageFont.truetype(font_path, 20)
                break
            except:
                continue
        else:
            base_font = ImageFont.load_default()
    except:
        base_font = ImageFont.load_default()
    
    for key, value in data.items():
        if key in fields_config and value:  # Пропускаем пустые значения
            config = fields_config[key]
            font = ImageFont.truetype(font_path, config["font_size"]) if font_path else base_font
            
            x, y = config["coords"]
            text = str(value)
            
            if config.get("center", False):
                # Центрирование текста
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                x = x - text_width // 2
            
            draw.text((x, y), text, font=font, fill=config["color"])
    
    img.save(output_path)
    return True


def main():
    # Ваши данные
    data = {
        "hospital_name": "ГБУЗ ГП Поликлиника №7",
        "full_name": "Hello world",
        "datetime": "02/02/2026 12:34",
        "docktor_type": "",
        "docktor_naem": "Alex"
    }
    

    # Создаем билет
    success = create_ticket(data, "/app_files/media/templates/template_docktor_ticket.jpg", "/app_files/media/templates/template_docktor_ticket.jpg")
    
    if success:
        # Открываем результат (если нужно)
        try:
            img = Image.open("ticket.jpg")
            img.show()
        except:
            pass


if __name__ == "__main__":
    main()