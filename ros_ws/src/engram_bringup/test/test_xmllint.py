from pathlib import Path

import pytest
from ament_xmllint.main import main


@pytest.mark.linter
@pytest.mark.xmllint
def test_xmllint() -> None:
    package_dir = Path(__file__).resolve().parents[1]
    assert main(argv=[str(package_dir / 'package.xml')]) == 0, 'package.xml failed schema check'
