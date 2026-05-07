import random
import re
from io import BytesIO

from django import forms
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_ANCHOR,
    AVATAR_COLORS,
    AVATAR_FONT_SIZE,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    AVATAR_TEXT_Y_OFFSET,
)


def normalize_phone(phone):
    phone = phone.strip()

    if re.fullmatch(r"8\d{10}", phone):
        return "+7" + phone[1:]

    if re.fullmatch(r"\+7\d{10}", phone):
        return phone

    raise forms.ValidationError(
        "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
    )


def generate_avatar(name):
    letter = (name[:1] or "U").upper()
    image = Image.new("RGB", AVATAR_SIZE, random.choice(AVATAR_COLORS))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox(AVATAR_ANCHOR, letter, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    position = (
        (AVATAR_SIZE[0] - width) / 2,
        (AVATAR_SIZE[1] - height) / 2 - AVATAR_TEXT_Y_OFFSET,
    )
    draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return ContentFile(buffer.getvalue(), name=f"avatar_{letter}.png")
