from enum import Enum


class FileType(Enum):
    PHOTO_JPEG = "image/jpeg"
    PHOTO_PNG = "image/png"
    PHOTO_GIF = "image/gif"
    PHOTO_SVG = "image/svg+xml"
    PHOTO_WEBP = "image/webp"

    VIDEO_MP4 = "video/mp4"

    AUDIO_MP3 = "audio/mpeg"
    AUDIO_OGG = "audio/ogg"
    AUDIO_WAV = "audio/wav"

    TEXT_PLAIN = "text/plain"

    APPLICATION_PDF = "application/pdf"
    APPLICATION_ZIP = "application/zip"
    APPLICATION_X_TAR = "application/x-tar"
