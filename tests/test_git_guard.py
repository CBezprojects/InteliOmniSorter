from src.safety.git_guard import classify_git_status, parse_git_status_output


def test_classify_git_status():
    assert classify_git_status("??") == "git untracked file"
    assert classify_git_status(" M") == "git modified file"
    assert classify_git_status("M ") == "git staged change"
    assert classify_git_status("A ") == "git staged change"


def test_parse_git_status_output():
    output = "\n".join(
        [
            "?? src/actions/new_file.py",
            " M src/terminal/cli.py",
            "M  tests/test_git_guard.py",
        ]
    )

    result = parse_git_status_output(output)

    assert result["src/actions/new_file.py"]["reason"] == "git untracked file"
    assert result["src/terminal/cli.py"]["reason"] == "git modified file"
    assert result["tests/test_git_guard.py"]["reason"] == "git staged change"
