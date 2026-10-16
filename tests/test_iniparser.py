import os

import pytest

import pyskooltest  # Puts PYSKOOL_HOME on sys.path
from pyskool.iniparser import IniParser

def test_path_not_found(capsys, tmp_path):
    # The given path is neither a file nor a directory, so the parser reports
    # an error and exits (without changing the current working directory)
    path = str(tmp_path / 'missing.ini')
    cwd = os.getcwd()

    with pytest.raises(SystemExit) as e:
        IniParser(path)
    assert e.value.code == 1
    assert capsys.readouterr() == ('', f'{path}: file or directory not found\n')
    assert os.getcwd() == cwd

def test_add_to_existing_section(tmp_path):
    # A section name ending with '+' adds lines to the section of that name
    # (whether it was defined earlier in the same file or in an earlier file),
    # or creates the section if it hasn't been defined yet; a section name
    # without '+' replaces any section of that name
    (tmp_path / 'a.ini').write_text(
        '[Colours]\n'
        'red\n'
        '[Shapes]\n'
        'square\n'
        '[Colours+]\n'
        'green\n'
    )
    (tmp_path / 'b.ini').write_text(
        '[Colours+]\n'
        'blue\n'
        '[Sizes+]\n'
        'small\n'
        '[Shapes]\n'
        'circle\n'
    )

    parser = IniParser(str(tmp_path), False)
    assert list(parser.sections.items()) == [
        ('Colours', ['red', 'green', 'blue']),
        ('Shapes', ['circle']),
        ('Sizes', ['small'])
    ]
