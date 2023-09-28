from dataclasses import dataclass
from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator, TranslatorRunner

from config import settings

ru_file_path = Path('tgbot/localization/locales/ru.ftl')
en_file_path = Path('tgbot/localization/locales/en.ftl')


@dataclass
class Translator:
    global_lang: str = settings.GLOBAL_LANG_CODE

    t_hub: TranslatorHub = TranslatorHub(
        {settings.RU_LANG_CODE: (settings.RU_LANG_CODE, settings.EN_LANG_CODE),
         settings.EN_LANG_CODE: (settings.EN_LANG_CODE,)},
        translators=[
            FluentTranslator(locale=settings.EN_LANG_CODE,
                             translator=FluentBundle.from_files(
                                 "en-US",
                                 filenames=[en_file_path],
                                 # use_isolating=False
                             )),

            FluentTranslator(locale=settings.RU_LANG_CODE,
                             translator=FluentBundle.from_files(
                                 "ru-RU",
                                 filenames=[ru_file_path],
                                 # use_isolating=False
                             ))],
        root_locale=settings.GLOBAL_LANG_CODE,
    )

    # def __call__(self, language: str, *args, **kwargs):
    #     return LocalizedTranslator(translator=self.t_hub.get_translator_by_locale(language))


class LocalizedTranslator:
    translator: TranslatorRunner

    def __init__(self, translator) -> None:
        self.translator = translator

    def get(self, key: str, **kwargs: dict) -> str:
        return self.translator.get(key, **kwargs)
