# app/bootstrap/lifespan.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.bootstrap.parser import ConfigParser
from app.bootstrap.scanner import Scanner
from app.bootstrap.loader import Loader
from app.bootstrap.wiring import wire_lifecycle_management
from app.bootstrap.state import init_lifecycle_manager
from app.bootstrap.lifecycle import (
    startup_state,
    shutdown_state,
)
from app.di.registry import METADATA_REGISTRY
from app.di.builder import ContainerBuilder
from app.di.container import DependencyContainer
from app.routing.builder import RouteBuilder
from components.infrastructure.console_log_sink import ConsoleLogSink
from components.infrastructure.event_bus import ASyncEventBus
from components.infrastructure.system_logger import SystemLogger
from config.settings import app_settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    # --- Bootstrap phase ---
    try:
        # --- Init Core ---
        event_bus = ASyncEventBus()
        log_sink = ConsoleLogSink(event_bus=event_bus)
        logger = SystemLogger(bus=event_bus)

        manager = init_lifecycle_manager(app=app)
        scanner = Scanner()

        # --- Scan Components ---
        scanner.scan_packages([
            app_settings.SERVICE_PACKAGE_NAME,
            app_settings.CONTROLLER_PACKAGE_NAME,
        ])
        scanner.import_scanned_modules()

        # --- Load Config ---
        parser = ConfigParser(registry=METADATA_REGISTRY)
        loader = Loader(parser=parser.parse_config)
        config = loader.load_from_path(path=app_settings.CONFIG_FILE_PATH)


        # --- Wire Components ---
        container = DependencyContainer()
        container_builder = ContainerBuilder(container=container,
                                             registry=METADATA_REGISTRY,
                                             config=config,
                                             logger=logger,)

        container_builder.build()

        wire_lifecycle_management(container=container,
                                  manager=manager)


        # --- Build Routes ---
        builder = RouteBuilder(app=app,
                               container=container)
        builder.build_api_routes(registry=METADATA_REGISTRY)

        await startup_state(app=app)

        yield # control back to fastAPI

    # -- Shutdown phase ---
    finally:
        await shutdown_state(app=app)
