from urllib.parse import urlparse
from rest_framework.serializers import ValidationError


class YoutubeValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url = value.get(self.field)
        if url:
            host = urlparse(url).hostname
            if host not in ('youtube.com', 'www.youtube.com'):
                raise ValidationError('Разрешены только ссылки на youtube.com')