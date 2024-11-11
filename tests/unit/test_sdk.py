from pathlib import Path
from typing import Any

import pytest

from drasi_reaction.models.events import (ChangeEvent, ControlEvent,
                                          UpdatedResult)
from drasi_reaction.sdk import DrasiReaction
from drasi_reaction.utils import yaml_query_configs

SUBSCRIBE_QUERIES = {"query1": "foo: bar"}

DELETE_EVENT = {
    "addedResults": [],
    "updatedResults": [],
    "deletedResults": [{"Id": 1, "Name": "Bar"}],
    "kind": "change",
}

ADDED_EVENT = {
    "addedResults": [{"Id": 1, "Name": "Foo"}],
    "updatedResults": [],
    "deletedResults": [],
    "kind": "change",
}

UPDATED_EVENT = {
    "addedResults": [],
    "updatedResults": [
        {"before": {"Id": 1, "Name": "Foo"}, "after": {"Id": 1, "Name": "Bar"}}
    ],
    "deletedResults": [],
    "kind": "change",
}


async def mock_on_change_event(
    data: ChangeEvent, query_configs: dict[Any, Any] | None = None
):
    ...


async def mock_on_control_event(
    data: ControlEvent, query_configs: dict[Any, Any] | None = None
):
    ...


@pytest.fixture(scope="session")
def query_config_dir(tmp_path_factory):
    mock_dir = tmp_path_factory.mktemp("queries")
    for query, content in SUBSCRIBE_QUERIES.items():
        qconfig: Path = mock_dir / query
        qconfig.write_text(content)
    return mock_dir


def test_drasi_reaction(query_config_dir):
    reaction = DrasiReaction(
        on_change_event=mock_on_change_event,
        on_control_event=mock_on_control_event,
        parse_query_configs=yaml_query_configs,
    )

    reaction.config_directory = query_config_dir

    reaction.subscribe()

    qconfigs = reaction.query_configs

    # test to validate configs are read
    assert "query1" in qconfigs.keys()
    assert {"foo": "bar"} == qconfigs.get("query1")

    # test that /query1 was read and added to the router
    assert any([route.path == "/query1" for route in reaction._app.router.routes])


def test_updated_result():
    data = {
        "before": {"key1": "value1"},
        "after": {"key1": "new_value1"},
    }
    updated_result = UpdatedResult(**data)
    assert updated_result.before == {"key1": "value1"}
    assert updated_result.after == {"key1": "new_value1"}

    # handle extra fields
    extra_data = {"extra_field": "extra_value"}
    updated_result_with_extra = UpdatedResult(**data, **extra_data)
    assert updated_result_with_extra.extra_field == "extra_value"


def test_change_event_alias_handling():
    data = {
        "kind": "change",
        "addedResults": [{"id": 1}],
        "deletedResults": [{"id": 2}],
        "updatedResults": [{"before": {"id": 1}, "after": {"id": 2}}],
    }
    change_event = ChangeEvent(**data)
    assert change_event.added_results == [{"id": 1}]
    assert change_event.deleted_results == [{"id": 2}]
    assert isinstance(change_event.updated_results[0], UpdatedResult)

    serialized_data = change_event.model_dump(by_alias=True)
    assert "addedResults" in serialized_data
    assert "deletedResults" in serialized_data
    assert "updatedResults" in serialized_data


def test_change_event_with_extra_fields():
    data = {
        "kind": "change",
        "addedResults": [{"id": 1}],
        "extra_field": "extra_value",
    }
    change_event = ChangeEvent(**data)
    assert change_event.extra_field == "extra_value"


def test_control_event_alias_handling():
    data = {"kind": "control", "controlSignal": {"kind": "test_signal"}}
    control_event = ControlEvent(**data)
    assert control_event.control_signal.kind == "test_signal"

    serialized_data = control_event.model_dump(by_alias=True)
    assert "controlSignal" in serialized_data
    assert serialized_data["controlSignal"]["kind"] == "test_signal"
