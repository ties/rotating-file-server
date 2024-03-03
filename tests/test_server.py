import logging
from pathlib import Path

import pytest

from rotate_files.server import Server


@pytest.mark.asyncio
async def test_app(tmp_path: Path, aiohttp_client):
    """Integration test using pytest-aiohttp."""
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"

    with f1.open("w", encoding="utf8") as f:
        f.write("First file.")
    with f2.open("w", encoding="utf8") as f:
        f.write("Second file.")

    subject = Server(files=[f1, f2], port=8000, random=False)
    assert subject.port == 8000

    client = await aiohttp_client(subject.application)

    # first request
    resp = await client.get("/json")

    assert resp.status == 200
    text = await resp.text()
    assert "First file." in text

    # second
    resp = await client.get("/json")

    assert resp.status == 200
    text = await resp.text()
    assert "Second file." in text

    # and cycles
    resp = await client.get("/json")

    assert resp.status == 200
    text = await resp.text()
    assert "First file." in text


@pytest.mark.asyncio
async def test_glob(tmp_path: Path, aiohttp_client, caplog):
    """Integration test for a config with globs."""
    caplog.set_level(logging.DEBUG)

    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"

    with f1.open("w", encoding="utf8") as f:
        f.write("First file.")
    with f2.open("w", encoding="utf8") as f:
        f.write("Second file.")

    subject = Server(files=[str(tmp_path / "*.txt")], port=8000, random=False)
    assert subject.port == 8000

    client = await aiohttp_client(subject.application)

    payloads = set()
    # first request
    resp = await client.get("/file")

    assert resp.status == 200
    text = await resp.text()
    payloads.add(text)

    # second
    resp = await client.get("/json")
    assert resp.status == 200
    text = await resp.text()
    assert text not in payloads


@pytest.mark.asyncio
async def test_random_permutation(tmp_path: Path, aiohttp_client, caplog):
    """Integration test for a config with globs."""
    caplog.set_level(logging.DEBUG)

    targets = []
    for x in range(100):
        f = tmp_path / f"f{x}.txt"
        targets.append(f)
        with f.open("w", encoding="utf8") as f:
            f.write(f"{x}")

    subject = Server(files=targets, port=8000, random=True)
    assert subject.port == 8000

    client = await aiohttp_client(subject.application)

    payloads = set()
    for x in range(100):
        # first request
        resp = await client.get("/file")

        assert resp.status == 200
        text = await resp.text()

        payloads.add(text)

    assert len(payloads) < 97
    assert len(payloads) > 3
