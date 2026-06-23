from realestate_scraper.cli import main


def test_list_sites_outputs_json_lines(capsys) -> None:
    code = main(["list-sites", "--sources", "data/sources.yml", "--top", "2"])
    captured = capsys.readouterr()
    assert code == 0
    assert "base_url" in captured.out
