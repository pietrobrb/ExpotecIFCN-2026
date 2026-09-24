from datetime import date
from os import path

from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now
from shortuuid import uuid

@deconstructible
class FormatStringFileUpload:
    """FileField upload_to function that use string format to get file name"""

    def __init__(self, template: str = None, date_format: bool = False):
        self.date_format = date_format
        self.template = template or ""

    def __call__(self, instance, filename) -> str:
        random_text = get_random_string(16)
        basename, ext = path.splitext(filename)
        upload_path = self.template.format(
            filename=filename,
            instance=instance,
            basename=basename,
            ext=ext[1:],
            random_text=random_text,
            shortuuid=uuid(),
        )
        if self.date_format:
            return now().strftime(upload_path)
        return upload_path

def get_current_year_str():
    return str(date.today().year)