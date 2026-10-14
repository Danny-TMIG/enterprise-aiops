"""i18n: locale-aware formatting + message catalog."""

from dcs.generate import requirement  # pragma: no cover

CATALOG = {
    "en": {"greeting": "Hello, {name}"},
    "es": {"greeting": "Hola, {name}"},
    "ja": {"greeting": "こんにちは、{name}"},
}


def t(locale: str, key: str, **kw) -> str:  # pragma: no cover
    cat = CATALOG.get(locale) or CATALOG["en"]
    template = cat.get(key) or CATALOG["en"].get(key) or key
    return template.format(**kw)  # pragma: no cover


@requirement(
    id="DCS-XC-I18N-001",
    title="message catalog falls back to English",
    section="X.i18n",
    hats=["FE", "TW", "DA"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert t("es", "greeting", name="Ana") == "Hola, Ana"
    assert t("zz", "greeting", name="Sam") == "Hello, Sam"
    assert t("en", "unknown.key") == "unknown.key"
