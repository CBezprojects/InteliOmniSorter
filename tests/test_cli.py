from src.terminal.cli import build_parser


def test_cli_has_scan_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["scan", "."])
    assert args.command == "scan"
    assert args.path == "."
