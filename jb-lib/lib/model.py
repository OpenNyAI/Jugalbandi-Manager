from enum import Enum


class LanguageCodes(Enum):
    EN = "English"
    HI = "Hindi"
    BN = "Bengali"
    GU = "Gujarati"
    MR = "Marathi"
    OR = "Oriya"
    PA = "Punjabi"
    KN = "Kannada"
    ML = "Malayalam"
    TA = "Tamil"
    TE = "Telugu"
    AF = "Afrikaans"
    AR = "Arabic"
    ZH = "Chinese"
    FR = "French"
    DE = "German"
    ID = "Indonesian"
    IT = "Italian"
    JA = "Japanese"
    KO = "Korean"
    PT = "Portuguese"
    RU = "Russian"
    ES = "Spanish"
    TR = "Turkish"


class InternalServerException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 500

    def __str__(self):
        return self.message
