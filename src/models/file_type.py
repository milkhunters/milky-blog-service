from enum import Enum


class FileType(str, Enum):
    VIDEO_MP4 = "video/mp4"
    VIDEO_MPEG = "video/mpeg"
    VIDEO_WEBM = "video/webm"
    VIDEO_OGG = "video/ogg"
    PHOTO_JPEG = "image/jpeg"
    PHOTO_PNG = "image/png"
    PHOTO_GIF = "image/gif"
    AUDIO_MPEG = "audio/mpeg"
    AUDIO_OGG = "audio/ogg"
    AUDIO_WAV = "audio/wav"
    AUDIO_WEBM = "audio/webm"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    TEXT_CSS = "text/css"
    TEXT_JAVASCRIPT = "text/javascript"
    APPLICATION_PDF = "application/pdf"
    APPLICATION_ZIP = "application/zip"
    APPLICATION_JSON = "application/json"
    APPLICATION_MSWORD = "application/msword"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
