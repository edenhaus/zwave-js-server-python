"""Test the dump helper."""
from unittest.mock import call

import pytest

from zwave_js_server.dump import dump_msgs

from .common import update_ws_client_msg_queue


@pytest.fixture(name="event")
def event_fixture():
    """Return a received event from the websocket client."""
    return {
        "type": "event",
        "event": {
            "source": "node",
            "event": "value updated",
            "nodeId": 52,
            "args": {
                "commandClassName": "Basic",
                "commandClass": 32,
                "endpoint": 0,
                "property": "currentValue",
                "newValue": 255,
                "prevValue": 255,
                "propertyName": "currentValue",
            },
        },
    }


async def test_dump(
    client_session,
    result,
    url,
    version_data,
    set_api_schema_data,
    ws_client,
):
    """Test the dump function."""
    update_ws_client_msg_queue(ws_client, (version_data, set_api_schema_data, result))
    messages = await dump_msgs(url, client_session)

    assert ws_client.receive_json.call_count == 3
    assert ws_client.send_json.call_count == 2
    assert ws_client.send_json.call_args == call(
        {"command": "start_listening", "messageId": "listen-id"}
    )
    assert ws_client.close.call_count == 1
    assert messages
    assert len(messages) == 3
    assert messages[0] == version_data
    assert messages[1] == set_api_schema_data
    assert messages[2] == result


async def test_dump_timeout(
    client_session,
    result,
    url,
    event,
    version_data,
    set_api_schema_data,
    ws_client,
):
    """Test the dump function with timeout."""
    update_ws_client_msg_queue(
        ws_client, (version_data, set_api_schema_data, result, event)
    )
    messages = await dump_msgs(url, client_session, 0.05)

    assert ws_client.receive_json.call_count == 5
    assert ws_client.send_json.call_count == 2
    assert ws_client.send_json.call_args == call(
        {"command": "start_listening", "messageId": "listen-id"}
    )
    assert ws_client.close.call_count == 1
    assert messages
    assert len(messages) == 4
    assert messages[0] == version_data
    assert messages[1] == set_api_schema_data
    assert messages[2] == result
    assert messages[3] == event
