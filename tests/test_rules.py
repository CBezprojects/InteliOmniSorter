from src.rules.rules_engine import build_plan, get_subtype, suggest_destination


def test_build_plan_basic():
    scan_result = {
        "scan_path": "/tmp/test",
        "files": [
            {
                "path": "/tmp/test/a.jpg",
                "name": "a.jpg",
                "category": "image",
                "suffix": ".jpg",
            },
            {
                "path": "/tmp/test/b.pdf",
                "name": "b.pdf",
                "category": "document",
                "suffix": ".pdf",
            },
        ],
    }

    plan = build_plan(scan_result)

    assert plan["total_files"] == 2
    assert plan["summary"]["by_category"]["image"] == 1
    assert plan["summary"]["by_category"]["document"] == 1
    assert any("/Images/jpeg/" in item["destination"] for item in plan["plan"])
    assert any("/Documents/pdf/" in item["destination"] for item in plan["plan"])


def test_hidden_file_goes_to_review_hidden():
    file_record = {
        "path": "/tmp/test/.gitignore",
        "name": ".gitignore",
        "category": "unknown",
        "suffix": "",
    }

    result = suggest_destination(file_record, "/tmp/test")
    assert "/Review/Hidden/.gitignore" in result["destination"]


def test_get_subtype_python():
    file_record = {
        "name": "main.py",
        "suffix": ".py",
    }
    assert get_subtype(file_record) == "python"
