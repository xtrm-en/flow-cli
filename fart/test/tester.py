# -*- coding: utf-8 -*-
import os
from fart.test.types import TestMetadata
from fart.utils import info


def parse_metadata(test_path: str) -> TestMetadata:
    base_dir = os.path.basename(__file__) / "testers"
    info(f"Looking for test metadata in '{base_dir}'")


def run_test(test_path: str) -> bool:
    test_metadata: TestMetadata = parse_metadata(test_path)
