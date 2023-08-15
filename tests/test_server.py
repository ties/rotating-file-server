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
    resp = await client.get('/json')

    assert resp.status == 200
    text = await resp.text()
    assert 'First file.' in text

    # second
    resp = await client.get('/json')

    assert resp.status == 200
    text = await resp.text()
    assert 'Second file.' in text
