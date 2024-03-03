import glob
import itertools
import logging
import random
from pathlib import Path
from typing import List

import click
import yaml
from aiohttp import web

LOG = logging.getLogger(__name__)

def expand_patterns(paths: Path | str) -> List[Path]:
    """Expand globs for the strings in a set of paths or strings"""
    res = []

    for input in paths:
        LOG.debug("Processing input: %s", input)
        match input:
            case Path():
                res.append(input)
            case str(p):
                res.extend(map(Path, glob.glob(p)))

    if len(res) < 100:
        LOG.debug("Effective files: %s", res)
    return res


class Server:
    """The simple webserver"""

    idx: int = 0
    files: List[Path]
    random: bool

    def __init__(self, files: List[str | Path], port: int, random: bool):
        self.port = port
        self.random = random
        self.files = expand_patterns(files)

    @property
    def application(self) -> web.Application:
        """Build the application"""
        app = web.Application()
        app.router.add_route("GET", "/{tail:.*}", self.serve_files)

        return app

    def run(self) -> None:
        """Start the webserver"""
        web.run_app(self.application, port=self.port)

    async def serve_files(self, req: web.BaseRequest) -> web.Response:
        """Serve all the files in sequence"""
        if self.random:
            effective_file = random.choice(self.files)
        else:
            effective_file = self.files[self.idx % len(self.files)]

        LOG.info(
            "Serving %s for idx=%d req=%s", effective_file.name, self.idx, req.path
        )

        self.idx += 1

        return web.FileResponse(effective_file)


@click.command()
@click.option("--config", default="config.yaml", help="Config file to use", type=click.Path(path_type=Path))
@click.option("--port", default=8080, help="Port to bind to")
@click.option("--port", default=8080, help="Port to bind to")
@click.option("--random/--in-order", default=False)
@click.option("-v", "--verbose", count=True)
def server_cli(config: Path, port: int, verbose: int, random: bool):
    """Start the webserver"""
    logging.basicConfig(level=logging.DEBUG if verbose > 0 else logging.INFO)

    with config.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    LOG.info(config)

    server = Server(config["files"], port, random)

    server.run()
