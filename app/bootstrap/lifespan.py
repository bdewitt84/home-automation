# app/bootstrap/lifespan.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
import traceback

from app.bootstrap.parser import ConfigParser
from app.bootstrap.scanner import Scanner
from app.bootstrap.loader import Loader
from app.bootstrap.wiring import wire_lifecycle_management
from app.bootstrap.state import init_lifecycle_manager
from app.bootstrap.lifecycle import (
    startup_state,
    shutdown_state,
)
from app.di.graph_builder import GraphBuilder
from app.di.graph_validator import GraphValidator
from app.di.registry import METADATA_REGISTRY
from app.di.container import DependencyContainer
from app.di.registry_builder import RegistryBuilder
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
        # TODO: container?

        await event_bus.start()
        await log_sink.start()

        scanner = Scanner(logger=logger)
        manager = init_lifecycle_manager(app=app)
        # TODO: assign core here?

    except Exception as e:
        print(f"Fatal framework error: Failed to initialize core. \n{e}\n{traceback.format_exc()}")
        raise

    try:
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
        core = [container, event_bus, log_sink, logger]
        registry_builder = RegistryBuilder(logger=logger,
                                           metadata=METADATA_REGISTRY,
                                           config=config,
                                           core=core)
        registry = registry_builder.build()
        graph_builder = GraphBuilder(logger=logger,
                                     registry=registry)
        dependency_graph = graph_builder.build_dependency_graph()
        graph_validator = GraphValidator(logger=logger,
                                         graph=dependency_graph)
        graph_validator.validate_graph()
        container._registry = registry

        # --- OLD WIRE COMPONENTS ---
        # TODO: Rework the lifecycle manager to take the registry?
        wire_lifecycle_management(container=container,
                                  manager=manager)

        # --- Build Routes ---
        builder = RouteBuilder(app=app,
                               container=container)
        builder.build_api_routes(registry=METADATA_REGISTRY)

        await startup_state(app=app)

        yield  # control back to fastAPI

    except Exception as e:
        logger.error(f"Fatal framework error: \n{e}\n{traceback.format_exc()}")
        raise

    # -- Shutdown phase ---
    finally:
        await event_bus.stop()
        await log_sink.stop()
        await shutdown_state(app=app)
