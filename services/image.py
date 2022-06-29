from PIL import Image


def resize_img(image_path, max_width=1280, max_height=1280):
    with Image.open(image_path) as img:
        _width, _height = img.size

        is_resizing = False
        if _width > max_width:
            w = _width / max_width
            _width /= w
            _height /= w
            is_resizing = True

        if _height > max_height:
            h = _height / max_height
            _height /= h
            _width /= h
            is_resizing = True

        if is_resizing:
            img.thumbnail((_width, _height))
            img.save(image_path)
