"""Test the 'synse.routes.aliases' Synse Server module's boot target route."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse.commands
import synse.validate
from synse import errors
from synse.routes.aliases import boot_target_route
from synse.scheme.base_response import SynseResponse
from tests import utils


def mockwritereturn(rack, board, device, data):
    """Mock method that will be used in monkeypatching the write command."""
    r = SynseResponse()
    r.data = {'data': data}
    return r


@pytest.fixture()
def mock_write(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.write, side_effect=mockwritereturn)
    monkeypatch.setattr(synse.commands, 'write', mock)
    return mock_write


def mockreadreturn(rack, board, device):
    """Mock method that will be used in monkeypatching the read command."""
    r = SynseResponse()
    r.data = {'value': 1}
    return r


@pytest.fixture()
def mock_read(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.read, side_effect=mockreadreturn)
    monkeypatch.setattr(synse.commands, 'read', mock)
    return mock_read


def mockvalidatedevicetype(device_type, rack, board, device):
    """Mock method that will be used in mokeypatching the validate device type method."""
    return


@pytest.fixture()
def mock_validate_device_type(monkeypatch):
    """Fixture to monkeypatch the validate_device_type method."""
    mock = asynctest.CoroutineMock(synse.validate.validate_device_type, side_effect=mockvalidatedevicetype)
    monkeypatch.setattr(synse.validate, 'validate_device_type', mock)
    return mock_validate_device_type


@pytest.mark.asyncio
async def test_synse_boot_target_read(mock_validate_device_type, mock_read, no_pretty_json):
    """Test a successful read."""

    r = utils.make_request('/synse/boot_target')

    result = await boot_target_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"value":1}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_boot_target_write_invalid(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing boot target with an invalid target specified."""

    r = utils.make_request('/synse/boot_target?target=test')

    try:
        await boot_target_route(r, 'rack-1', 'vec', '123456')
    except errors.SynseError as e:
        assert e.error_id == errors.INVALID_ARGUMENTS
        assert 'test' in e.args[0]


@pytest.mark.asyncio
async def test_synse_boot_target_write_valid_1(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing boot target with a valid target specified."""

    r = utils.make_request('/synse/boot_target?target=pxe')

    result = await boot_target_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"target","raw":"pxe"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_boot_target_write_valid_2(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing boot target with a valid target specified."""

    r = utils.make_request('/synse/boot_target?target=hdd')

    result = await boot_target_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"target","raw":"hdd"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_boot_target_route_bad_param(mock_validate_device_type, mock_write, no_pretty_json):
    """Test setting boot target, passing an unsupported query param."""

    r = utils.make_request('/synse/boot_target?unsupported=true')

    with pytest.raises(errors.InvalidArgumentsError):
        await boot_target_route(r, 'rack-1', 'vec', '123456')
