# src/pii/detector.py
# pyrefly: ignore [missing-import]
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
# pyrefly: ignore [missing-import]
from presidio_analyzer.nlp_engine import NlpEngineProvider
# pyrefly: ignore [missing-import]
from presidio_analyzer.predefined_recognizers import EmailRecognizer

def build_vietnamese_analyzer() -> AnalyzerEngine:
    # --- TASK 2.2.1 ---
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\b\d{11,12}\b",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        supported_language="vi",
        patterns=[cccd_pattern],
        context=["cccd", "căn cước", "chứng minh", "cmnd", "chứng minh thư"]
    )

    # --- TASK 2.2.2 ---
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"\b0?[35789]\d{8}\b",
            score=0.85
        )],
        context=["điện thoại", "sdt", "phone", "liên hệ", "di động"]
    )

    person_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_person",
            regex=r"\b[A-ZÀ-ỸA-Z][a-zà-ỹa-z]+(?:\s+[A-ZÀ-ỸA-Z][a-zà-ỹa-z]+)+\b",
            score=0.85
        )],
        context=["bệnh nhân", "họ tên", "tên", "bác sĩ", "ông", "bà", "anh", "chị"]
    )

    # --- TASK 2.2.3 ---
    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "vi", "model_name": "vi_core_news_lg"}]
    })
    nlp_engine = provider.create_engine()

    # --- TASK 2.2.4 ---
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["vi"])
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(person_recognizer)
    analyzer.registry.add_recognizer(EmailRecognizer(supported_language="vi"))

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    results = analyzer.analyze(
        text=str(text),
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
    )
    return results
