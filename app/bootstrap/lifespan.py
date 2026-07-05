# app/bootstrap/lifespan.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.bootstrap.scanner import scan_for_components

from app.bootstrap.wiring import (
    wire_infrastructure_components,
    wire_user_components,
    wire_lifecycle_management,
)

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
CONFIG_FILE_PATH = './config/config.json'


@asynccontextmanager
async def lifespan(app: FastAPI):

    # --- Bootstrap phase ---
    try:
        # --- Init Core ---
        container = init_dependency_container(app=app)
        container.register_self()
        manager = init_lifecycle_manager(app=app)

        # --- Load Config ---
        config_data = load_config_from_disk(path=CONFIG_FILE_PATH)

        # --- Scan and Wire Components ---
        scan_for_components(path=SERVICE_PACKAGE_NAME)

        wire_infrastructure_components(registry=COMPONENT_METADATA_REGISTRY,
                                       container=container)
        scan_for_components(path='api.controllers')

        container.validate_graph_dfs()

        wire_user_components(config_data=config_data,
                             container=container,
                             registry=COMPONENT_METADATA_REGISTRY)

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
