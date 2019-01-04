from conda_package_handling import cli

def test_cli_template():
    assert cli.cli() is None
