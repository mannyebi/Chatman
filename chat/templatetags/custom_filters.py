from django import template

register = template.Library()

@register.filter
def is_image(file_name):
    """return True if the file_name ends with one of the image_extenstions items. (return true if it is an image)
    """
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"] #image formats
    return any(file_name.lower().endswith(ext) for ext in image_extensions) #return true if the file name ends with one of image_extensions items.
