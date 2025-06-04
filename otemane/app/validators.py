import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        errors = []

        if len(password) < 10:
            errors.append("最低10文字以上必要です。")

        if not (re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'\d', password)):
            errors.append("アルファベットの大文字、小文字、数字をすべて含めてください。")

        if not re.search(r'[!@#$%&-]', password):
            errors.append("記号（例：! @ # $ % &）を1つ以上含めてください。")

        if re.search(r'(12345678|4567890|abcdefg|hijklmn|opqrstu|vwxyz)', password.lower()):
            errors.append("連続した数字や文字は使用できません。")

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "・最低10文字以上\n"
            "・大文字・小文字・数字を含める\n"
            "・記号（! @ # $ % &）を含める\n"
            "・連続した文字列を避ける"
        )
