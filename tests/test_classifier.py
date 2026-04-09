from src.classify.classifier import classify_path, classify_suffix, summarize_categories


def test_classify_known_image_suffix() -> None:
    result = classify_path("photo.JPG")
    assert result["suffix"] == ".jpg"
    assert result["category"] == "image"


def test_classify_known_document_suffix() -> None:
    result = classify_path("report.pdf")
    assert result["category"] == "document"


def test_classify_unknown_suffix() -> None:
    result = classify_path("mystery.xyzabc")
    assert result["category"] == "unknown"


def test_classify_no_extension() -> None:
    result = classify_path("README")
    assert result["suffix"] == ""
    assert result["category"] == "unknown"


def test_classify_suffix_direct() -> None:
    assert classify_suffix(".MP3") == "audio"


def test_summarize_categories() -> None:
    files = [
        {"category": "image"},
        {"category": "image"},
        {"category": "document"},
        {"category": "unknown"},
    ]
    summary = summarize_categories(files)
    assert summary["image"] == 2
    assert summary["document"] == 1
    assert summary["unknown"] == 1
