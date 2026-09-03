from topos_power.core.localization import LanguageManager


def test_supported_languages_have_core_labels():
    manager = LanguageManager()
    for language in ("zh_CN", "en_US"):
        manager.language = language
        assert manager.text("help")
        assert manager.text("tab_shutdown")
        assert manager.text("start")
