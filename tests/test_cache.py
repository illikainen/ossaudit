# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause
#
# pylint: disable=protected-access

import json
import tempfile
import time
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from ossaudit import cache, const


class CacheTestCase(TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def _write_cache(dst: Path, timestamp: float, n: int = -1) -> None:
        src = Path("tests", "data", "vulns01.json")
        with src.open() as f:
            entries = json.load(f)

        for i, entry in enumerate(entries):
            if n == -1 or i < n:
                entry["time"] = timestamp
            else:
                entry["time"] = time.time()

        with dst.open("w") as f:
            json.dump(entries, f)


class TestGet(CacheTestCase):
    def test_no_cache(self) -> None:
        self.assertIsNone(cache.get("x"))

    def test_have_cached_entry(self) -> None:
        path = Path(self.tmp.name).joinpath("vulns01.json")
        self._write_cache(path, time.time())

        with patch("ossaudit.const.CACHE", path):
            entry = cache.get("pkg:pypi/requests@0.10.0") or {}

        self.assertEqual(entry["coordinates"], "pkg:pypi/requests@0.10.0")

    def test_have_old_cached_entry(self) -> None:
        path = Path(self.tmp.name).joinpath("vulns01.json")
        self._write_cache(path, time.time() + const.CACHE_TIME + 1)

        with patch("ossaudit.const.CACHE", path):
            entry = cache.get("pkg:pypi/requests@0.10.0")

        self.assertIsNone(entry)

    def test_missing_cached_entry(self) -> None:
        path = Path(self.tmp.name).joinpath("vulns01.json")
        self._write_cache(path, time.time())

        with patch("ossaudit.const.CACHE", path):
            entry = cache.get("pkg:pypi/abcd@0.10.0")

        self.assertIsNone(entry)


class TestSave(CacheTestCase):
    def test_mkdir(self) -> None:
        path = Path(self.tmp.name).joinpath("x", "y", "z", "vulns01.json")

        with patch("ossaudit.const.CACHE", path):
            cache.save({})
            self.assertTrue(path.parent.exists())

    def test_remove_old(self) -> None:
        path = Path(self.tmp.name).joinpath("vulns01.json")

        timestamp = time.time() + const.CACHE_TIME + 1000
        self._write_cache(path, timestamp)

        with path.open() as f:
            entry = next(
                x for x in json.load(f)
                if x["coordinates"] == "pkg:pypi/requests@0.10.0"
            )

        with patch("ossaudit.const.CACHE", path):
            cache.save(entry)

        with path.open() as f:
            updated = json.load(f)

        self.assertEqual(len(updated), 1)
        self.assertNotEqual(updated[0]["time"], timestamp)

    def test_remove_partially_old(self) -> None:
        path = Path(self.tmp.name).joinpath("vulns01.json")

        timestamp = time.time() + const.CACHE_TIME + 1000
        self._write_cache(path, timestamp, 2)

        with path.open() as f:
            entry = next(
                x for x in json.load(f)
                if x["coordinates"] == "pkg:pypi/requests@0.10.0"
            )

        with patch("ossaudit.const.CACHE", path):
            cache.save(entry)

        with path.open() as f:
            updated = json.load(f)

        self.assertEqual(len(updated), 2)
        self.assertNotEqual(updated[0]["time"], timestamp)


class TestIsValid(TestCase):
    def test_missing_time(self) -> None:
        self.assertFalse(cache._is_valid({}))

    def test_old(self) -> None:
        self.assertFalse(
            cache._is_valid({
                "time": time.time() + const.CACHE_TIME + 1
            })
        )

    def test_valid(self) -> None:
        self.assertTrue(cache._is_valid({"time": time.time()}))
