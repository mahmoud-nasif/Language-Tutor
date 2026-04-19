"""G2P conversion using phonemizer with espeak-ng backend."""

from polyglot.analysis.models import G2PResult, G2PWordResult, LanguageCode

PHONEMIZER_LANGUAGE_MAP: dict[LanguageCode, str] = {
    "en-US": "en-us",
    "de-DE": "de",
}


class PhonemizerG2PService:
    """Convert target text to IPA-like tokens using phonemizer."""

    def convert(self, sentence: str, language: LanguageCode) -> G2PResult:
        """Produce per-word IPA for a sentence."""
        tokens = [token for token in sentence.strip().split() if token]
        if not tokens:
            return G2PResult(sentence=sentence, words=[])

        from phonemizer import phonemize

        ipa_tokens = phonemize(
            tokens,
            language=PHONEMIZER_LANGUAGE_MAP[language],
            backend="espeak",
            strip=True,
            with_stress=True,
            preserve_punctuation=False,
            njobs=1,
        )

        words = [
            G2PWordResult(word=word, ipa=ipa) for word, ipa in zip(tokens, ipa_tokens, strict=False)
        ]
        return G2PResult(sentence=sentence, words=words)
