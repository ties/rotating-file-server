import logging
import random
from pathlib import Path
from typing import List

import click
import yaml
from aiohttp import web

LOG = logging.getLogger(__name__)


class Server:
    """The simple webserver"""
    idx: int = 0

    def __init__(self, files: List[Path], port: int, random: bool):
        self.files = files
        self.port = port
        self.random = random

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
            effective_file = self.files[random.randint(0, len(self.files) - 1)]
        else:
            effective_file = self.files[self.idx % len(self.files)]

        LOG.info(
            "Serving %s for idx=%d req=%s", effective_file.name, self.idx, req.path
        )
        
        self.idx += 1

        return web.FileResponse(effective_file)


@click.command()
@click.option("--config_file", default="config.yaml", help="Config file to use")
@click.option("--port", default=8080, help="Port to bind to")
@click.option("--port", default=8080, help="Port to bind to")
@click.option("--random/--in-order", default=False)
@click.option("-v", "--verbose", count=True)
def server_cli(config_file: Path, port: int, verbose: int, random: bool):
    """Start the webserver"""
    logging.basicConfig(level=logging.DEBUG if verbose > 0 else logging.INFO)

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    LOG.info(config)

    files = [Path(f) for f in config["files"]]
    server = Server(files, port, random)

    server.run()
