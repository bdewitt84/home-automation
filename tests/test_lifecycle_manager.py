# tests/lifecycle_manager.py

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, create_autospec, call

from app.lifecycle_manager import LifeCycleManager
from interfaces import LifecycleManagementInterface


def test_index_singleton_index_valid_interface():
    manager = LifeCycleManager()
    singleton_managed = create_autospec(LifecycleManagementInterface)

    manager.index_singleton(singleton_managed)

    assert singleton_managed in manager._singletons


def test_index_singleton_skip_invalid_interface():
    manager = LifeCycleManager()
    singleton_unmanaged = Mock()

    manager.index_singleton(singleton_unmanaged)

    assert singleton_unmanaged not in manager._singletons


def test_index_singleton_only_index_once():
    manager = LifeCycleManager()
    singleton_managed = create_autospec(LifecycleManagementInterface)

    manager.index_singleton(singleton_managed)

    # Raises when asked to index the same component twice
    with pytest.raises(ValueError):
        manager.index_singleton(singleton_managed)


async def test_start_registered_stops_on_first_failure():

    manager = LifeCycleManager()
    singleton_1_startable = create_autospec(LifecycleManagementInterface)
    singleton_2_unstartable = create_autospec(LifecycleManagementInterface)
    singleton_3_startable = create_autospec(LifecycleManagementInterface)

    singleton_1_startable.start = AsyncMock()
    singleton_2_unstartable.start = AsyncMock()
    singleton_3_startable.start = AsyncMock()

    singleton_2_unstartable.start.side_effect = Exception("Unable to start")

    manager._singletons = [
        singleton_1_startable,
        singleton_2_unstartable,
        singleton_3_startable,
    ]

    with pytest.raises(Exception):
        await manager.start_registered()

    # Manager catches exceptions and re-raises instead of continuing
    singleton_1_startable.start.assert_called_once()
    singleton_2_unstartable.start.assert_called_once()
    singleton_3_startable.start.assert_not_called()


async def test_stop_registered_continues_after_failure():
    manager = LifeCycleManager()
    singleton_1_stoppable = create_autospec(LifecycleManagementInterface)
    singleton_2_unstoppable = create_autospec(LifecycleManagementInterface)
    singleton_3_stoppable = create_autospec(LifecycleManagementInterface)

    singleton_1_stoppable.stop = AsyncMock()
    singleton_2_unstoppable.stop = AsyncMock()
    singleton_3_stoppable.stop = AsyncMock()

    singleton_2_unstoppable.stop.side_effect = Exception("Unable to stop")

    manager._singletons = [
        singleton_1_stoppable,
        singleton_2_unstoppable,
        singleton_3_stoppable,
    ]

    await manager.stop_registered()

    # Manager catches exceptions and calls stop on all singletons
    singleton_3_stoppable.stop.assert_called_once()
    singleton_2_unstoppable.stop.assert_called_once()
    singleton_1_stoppable.stop.assert_called_once()


async def test_stop_registered_executes_in_reverse_order():
    manager = LifeCycleManager()
    # Create mocks and give them names for easy identification in call logs
    singleton_1 = create_autospec(LifecycleManagementInterface, instance=True)
    singleton_2 = create_autospec(LifecycleManagementInterface, instance=True)

    # Attach mock calls to parent so we can track the order
    parent_mock = AsyncMock()
    parent_mock.attach_mock(singleton_1.stop, "singleton_1_stop")
    parent_mock.attach_mock(singleton_2.stop, "singleton_2_stop")

    # Inject singletons to manager state (white box)
    manager._singletons = [singleton_1, singleton_2]

    await manager.stop_registered()

    # calls to stop should happen in reverse order
    parent_mock.assert_has_calls([call.singleton_2_stop(), call.singleton_1_stop()], any_order=False)
