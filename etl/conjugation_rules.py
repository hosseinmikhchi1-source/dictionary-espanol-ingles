"""
Conjugation Rules - Phase 2
Build-time rule engine for Spanish verb conjugation.
Computes regular paradigms, detects irregularities, cross-checks sources.
Never used at runtime.
"""
import re


class ConjugationRules:
    """Spanish verb conjugation rule engine."""

    # Regular endings for -ar, -er, -ir verbs
    REGULAR_ENDINGS = {
        "ar": {
            "present": {"1sg": "o", "2sg": "as", "3sg": "a", "1pl": "amos", "2pl": "áis", "3pl": "an"},
            "preterite": {"1sg": "é", "2sg": "aste", "3sg": "ó", "1pl": "amos", "2pl": "asteis", "3pl": "aron"},
            "imperfect": {"1sg": "aba", "2sg": "abas", "3sg": "aba", "1pl": "ábamos", "2pl": "abais", "3pl": "aban"},
            "conditional": {"1sg": "aría", "2sg": "arías", "3sg": "aría", "1pl": "aríamos", "2pl": "aríais", "3pl": "arían"},
            "future": {"1sg": "aré", "2sg": "arás", "3sg": "ará", "1pl": "aremos", "2pl": "aréis", "3pl": "arán"},
            "present_subjunctive": {"1sg": "e", "2sg": "es", "3sg": "e", "1pl": "emos", "2pl": "éis", "3pl": "en"},
            "imperfect_subjunctive": {"1sg": "ara", "2sg": "aras", "3sg": "ara", "1pl": "áramos", "2pl": "arais", "3pl": "aran"},
            "imperfect_subjunctive_se": {"1sg": "ase", "2sg": "ases", "3sg": "ase", "1pl": "ásemos", "2pl": "aseis", "3pl": "asen"},
            "imperative_affirmative": {"2sg": "a", "3sg": "e", "1pl": "emos", "2pl": "ad", "3pl": "en"},
            "imperative_negative": {"2sg": "es", "3sg": "e", "1pl": "emos", "2pl": "éis", "3pl": "en"},
        },
        "er": {
            "present": {"1sg": "o", "2sg": "es", "3sg": "e", "1pl": "emos", "2pl": "éis", "3pl": "en"},
            "preterite": {"1sg": "í", "2sg": "iste", "3sg": "ió", "1pl": "imos", "2pl": "isteis", "3pl": "ieron"},
            "imperfect": {"1sg": "ía", "2sg": "ías", "3sg": "ía", "1pl": "íamos", "2pl": "íais", "3pl": "ían"},
            "conditional": {"1sg": "ería", "2sg": "erías", "3sg": "ería", "1pl": "eríamos", "2pl": "eríais", "3pl": "erían"},
            "future": {"1sg": "eré", "2sg": "erás", "3sg": "erá", "1pl": "eremos", "2pl": "eréis", "3pl": "erán"},
            "present_subjunctive": {"1sg": "a", "2sg": "as", "3sg": "a", "1pl": "amos", "2pl": "áis", "3pl": "an"},
            "imperfect_subjunctive": {"1sg": "iera", "2sg": "ieras", "3sg": "iera", "1pl": "iéramos", "2pl": "ierais", "3pl": "ieran"},
            "imperfect_subjunctive_se": {"1sg": "iese", "2sg": "ieses", "3sg": "iese", "1pl": "iésemos", "2pl": "ieseis", "3pl": "iesen"},
            "imperative_affirmative": {"2sg": "e", "3sg": "a", "1pl": "amos", "2pl": "ed", "3pl": "an"},
            "imperative_negative": {"2sg": "as", "3sg": "a", "1pl": "amos", "2pl": "áis", "3pl": "an"},
        },
        "ir": {
            "present": {"1sg": "o", "2sg": "es", "3sg": "e", "1pl": "imos", "2pl": "ís", "3pl": "en"},
            "preterite": {"1sg": "í", "2sg": "iste", "3sg": "ió", "1pl": "imos", "2pl": "isteis", "3pl": "ieron"},
            "imperfect": {"1sg": "ía", "2sg": "ías", "3sg": "ía", "1pl": "íamos", "2pl": "íais", "3pl": "ían"},
            "conditional": {"1sg": "iría", "2sg": "irías", "3sg": "iría", "1pl": "iríamos", "2pl": "iríais", "3pl": "irían"},
            "future": {"1sg": "iré", "2sg": "irás", "3sg": "irá", "1pl": "iremos", "2pl": "iréis", "3pl": "irán"},
            "present_subjunctive": {"1sg": "a", "2sg": "as", "3sg": "a", "1pl": "amos", "2pl": "áis", "3pl": "an"},
            "imperfect_subjunctive": {"1sg": "iera", "2sg": "ieras", "3sg": "iera", "1pl": "iéramos", "2pl": "ierais", "3pl": "ieran"},
            "imperfect_subjunctive_se": {"1sg": "iese", "2sg": "ieses", "3sg": "iese", "1pl": "iésemos", "2pl": "ieseis", "3pl": "iesen"},
            "imperative_affirmative": {"2sg": "e", "3sg": "a", "1pl": "amos", "2pl": "id", "3pl": "an"},
            "imperative_negative": {"2sg": "as", "3sg": "a", "1pl": "amos", "2pl": "áis", "3pl": "an"},
        },
    }

    # Stem-changing patterns
    STEM_CHANGES = {
        "e->ie": re.compile(r"^(.+?)e(.+)$"),
        "o->ue": re.compile(r"^(.+?)o(.+)$"),
        "e->i": re.compile(r"^(.+?)e(.+)$"),
        "u->ue": re.compile(r"^(.+?)u(.+)$"),
    }

    # Irregular verbs (most common)
    IRREGULAR_VERBS = {
        "ser", "estar", "ir", "haber", "tener", "hacer", "decir",
        "poder", "querer", "saber", "dar", "ver", "poner",
        "traer", "caer", "oír", "construir", "conducir", "leer",
    }

    # Stem-changing verbs (e->ie, o->ue, e->i, u->ue)
    STEM_CHANGING_VERBS = {
        "pensar", "dormir", "pedir", "jugar", "empezar", "entender",
        "perder", "mentir", "sentir", "preferir", "sugerir",
        "poder", "volver", "resolver", "mover", "doler", "llover",
        "contar", "encontrar", "recordar", "volar", "costar",
        "servir", "repetir", "vestir", "elegir", "corregir",
        "conseguir", "seguir", "decir", "reír", "sonreír",
    }

    def __init__(self):
        pass

    def get_conjugation_class(self, infinitive: str) -> str:
        """Determine conjugation class from infinitive."""
        if infinitive.endswith("ar"):
            return "ar"
        elif infinitive.endswith("er"):
            return "er"
        elif infinitive.endswith("ir"):
            return "ir"
        return "unknown"

    def is_irregular(self, infinitive: str) -> bool:
        """Check if a verb is known to be irregular."""
        return infinitive in self.IRREGULAR_VERBS

    def get_stem(self, infinitive: str) -> str:
        """Get the stem of a verb."""
        if infinitive.endswith(("ar", "er", "ir")):
            return infinitive[:-2]
        return infinitive

    def compute_regular_form(self, infinitive: str, tense: str, person: str) -> str:
        """Compute a regular conjugation form."""
        conj_class = self.get_conjugation_class(infinitive)
        if conj_class == "unknown":
            return ""

        stem = self.get_stem(infinitive)
        endings = self.REGULAR_ENDINGS.get(conj_class, {})
        tense_endings = endings.get(tense, {})
        ending = tense_endings.get(person, "")

        if not ending:
            return ""

        # Apply stem changes for present tense
        if tense == "present" and person in ("1sg", "2sg", "3sg", "3pl"):
            stem = self._apply_stem_change(stem, infinitive)

        return stem + ending

    def _apply_stem_change(self, stem: str, infinitive: str) -> str:
        """Apply stem-changing patterns only for known stem-changing verbs."""
        if infinitive not in self.STEM_CHANGING_VERBS:
            return stem

        # e->ie (pensar -> piens-)
        if re.search(r"e", stem):
            idx = stem.rfind('e')
            if idx > 0:
                return stem[:idx] + "ie" + stem[idx+1:]
        # o->ue (dormir -> duerm-)
        if re.search(r"o", stem):
            idx = stem.rfind('o')
            if idx > 0:
                return stem[:idx] + "ue" + stem[idx+1:]
        return stem

    def compute_non_finite(self, infinitive: str) -> dict:
        """Compute non-finite forms."""
        conj_class = self.get_conjugation_class(infinitive)
        stem = self.get_stem(infinitive)

        if conj_class == "ar":
            return {
                "infinitive": infinitive,
                "gerund": stem + "ando",
                "past_participle": stem + "ado",
            }
        elif conj_class in ("er", "ir"):
            return {
                "infinitive": infinitive,
                "gerund": stem + "iendo",
                "past_participle": stem + "ido",
            }
        return {"infinitive": infinitive, "gerund": "", "past_participle": ""}

    def get_irregularity_signature(self, infinitive: str) -> str:
        """Get a signature for grouping similar irregular verbs."""
        if not self.is_irregular(infinitive):
            return ""
        # Simplified: return the verb itself as signature
        return infinitive

    def cross_check(self, source1_forms: dict, source2_forms: dict) -> list:
        """Cross-check two conjugation sources and return disagreements."""
        disagreements = []
        for key in set(source1_forms.keys()) & set(source2_forms.keys()):
            if source1_forms[key] != source2_forms[key]:
                disagreements.append({
                    "form": key,
                    "source1": source1_forms[key],
                    "source2": source2_forms[key],
                })
        return disagreements


# Golden verbs for testing
GOLDEN_VERBS = [
    "hablar", "tomar", "comer", "beber", "vivir", "escribir",
    "ser", "estar", "ir", "haber", "tener", "hacer",
    "decir", "poder", "querer", "saber", "dar", "ver",
    "pensar", "dormir", "pedir", "jugar",
    "buscar", "llegar", "empezar", "conocer", "construir", "conducir", "leer",
    "lavarse", "levantarse",
]


def test_conjugation():
    """Test conjugation rules."""
    rules = ConjugationRules()

    # Test regular -ar verb
    assert rules.compute_regular_form("hablar", "present", "1sg") == "hablo"
    assert rules.compute_regular_form("hablar", "present", "3sg") == "habla"
    assert rules.compute_regular_form("hablar", "preterite", "1sg") == "hablé"

    # Test regular -er verb
    assert rules.compute_regular_form("comer", "present", "1sg") == "como"
    assert rules.compute_regular_form("comer", "present", "3sg") == "come"

    # Test regular -ir verb
    assert rules.compute_regular_form("vivir", "present", "1sg") == "vivo"
    assert rules.compute_regular_form("vivir", "present", "3sg") == "vive"

    # Test non-finite forms
    non_finite = rules.compute_non_finite("hablar")
    assert non_finite["gerund"] == "hablando"
    assert non_finite["past_participle"] == "hablado"

    non_finite = rules.compute_non_finite("comer")
    assert non_finite["gerund"] == "comiendo"
    assert non_finite["past_participle"] == "comido"

    # Test irregular detection
    assert rules.is_irregular("ser") is True
    assert rules.is_irregular("hablar") is False

    # Test stem changes
    assert rules.compute_regular_form("pensar", "present", "1sg") == "pienso"
    assert rules.compute_regular_form("dormir", "present", "1sg") == "duermo"

    print("All conjugation tests passed!")


if __name__ == "__main__":
    test_conjugation()
