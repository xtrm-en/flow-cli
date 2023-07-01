# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Optional

from fart.test.types import TestMetadata


base_dirs: list[Path] = [
    Path(os.path.dirname(__file__)).parent / "testers"
]


def find_metadata(test_path: str) -> Optional[TestMetadata]:
    base_dirs: list[Path] = [
        Path(os.path.dirname(__file__))
    ]

    return None

def run_test(test_path: str) -> bool:
    test_metadata: TestMetadata = find_metadata(test_path)
    return False
