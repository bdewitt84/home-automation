# app/bootstrap/lifespan.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.bootstrap.scanner import Scanner

from app.bootstrap.wiring import (
    wire_infrastructure_components,
    wire_user_components,
    wire_lifecycle_management,
)
from app.di.builder import ContainerBuilder

from app.routing.builder import RouteBuilder

from app.bootstrap.config import load_config_from_disk

from app.bootstrap.state import (
    init_dependency_container,
    init_lifecycle_manager,
)

from app.bootstrap.lifecycle import startup_state, shutdown_state
from app.di.registry import COMPONENT_METADATA_REGISTRY


#todo: place these in app settings?
SERVICE_PACKAGE_NAME = 'components'
CONTROLLER_PACKAGE_NAME = 'api.v1.controllers'
CONFIG_FILE_PATH = './config/config.json'


@asynccontextmanager
async def lifespan(app: FastAPI):

    # --- Bootstrap phase ---
    try:
        # --- Init Core ---
        manager = init_lifecycle_manager(app=app)
        scanner = Scanner()

        # --- Load Config ---
        config_data = load_config_from_disk(path=CONFIG_FILE_PATH)

        # --- Scan and Wire Components ---
        scanner.scan_packages([
            SERVICE_PACKAGE_NAME,
            CONTROLLER_PACKAGE_NAME,
        ])
        scanner.import_scanned_modules()

        container_builder = ContainerBuilder(registry=COMPONENT_METADATA_REGISTRY,
                                             config=config_data,)
        container = container_builder.build()

        wire_lifecycle_management(container=container,
                                  manager=manager)

        builder = RouteBuilder(app=app,
                               container=container)
        builder.build_api_routes(registry=COMPONENT_METADATA_REGISTRY)

        await startup_state(app=app)

        yield # control back to fastAPI

    # -- Shutdown phase ---
    finally:
        await shutdown_state(app=app)
