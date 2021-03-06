"""Test the 'synse.commands.transaction' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long


import asynctest
import grpc
import pytest
from synse_plugin import api

import synse.cache
from synse import errors, plugin
from synse.commands.transaction import check_transaction
from synse.proto.client import SynseInternalClient
from synse.scheme.transaction import (TransactionListResponse,
                                      TransactionResponse)


def mockgettransaction(transaction):
    """Mock method to monkeypatch the get_transaction method."""
    # here, we hijack the 'transaction' input and make it the name of the plugin.
    # this allows us to use different plugin names when we are testing.
    return {
        'plugin': transaction,
        'context': {
            'action': 'foo',
            'raw': [b'bar']
        }
    }


def mockchecktransaction(self, transaction_id):
    """Mock method to monkeypatch the client check_transaction method."""
    return api.WriteResponse(
        created='october',
        updated='november',
        status=3,
        state=0,
    )


def mockchecktransactionfail(self, transaction_id):
    """Mock method to monkeypatch the client check_transaction method to fail."""
    raise grpc.RpcError()


@pytest.fixture()
def mock_get_transaction(monkeypatch):
    """Fixture to monkeypatch the cache transaction lookup."""
    mock = asynctest.CoroutineMock(synse.cache.get_transaction, side_effect=mockgettransaction)
    monkeypatch.setattr(synse.cache, 'get_transaction', mock)
    return mock_get_transaction


@pytest.fixture()
def mock_client_transaction(monkeypatch):
    """Fixture to monkeypatch the grpc client's transaction method."""
    monkeypatch.setattr(SynseInternalClient, 'check_transaction', mockchecktransaction)
    return mock_client_transaction


@pytest.fixture()
def mock_client_transaction_fail(monkeypatch):
    """Fixture to monkeypatch the grpc client's transaction method to fail."""
    monkeypatch.setattr(SynseInternalClient, 'check_transaction', mockchecktransactionfail)
    return mock_client_transaction_fail


@pytest.fixture()
def make_plugin():
    """Fixture to create and register a plugin for testing."""

    # make a dummy plugin for the tests to use
    if 'foo' not in plugin.Plugin.manager.plugins:
        plugin.Plugin('foo', 'localhost:9999', 'tcp')

    yield

    if 'foo' in plugin.Plugin.manager.plugins:
        del plugin.Plugin.manager.plugins['foo']

@pytest.mark.asyncio
async def test_transaction_command_no_plugin_name(mock_get_transaction):
    """Get a TransactionResponse when the plugin name doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction(None)
    except errors.SynseError as e:
        assert e.error_id == errors.TRANSACTION_NOT_FOUND


@pytest.mark.asyncio
async def test_transaction_command_no_plugin(mock_get_transaction):
    """Get a TransactionResponse when the plugin doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction('bar')
    except errors.SynseError as e:
        assert e.error_id == errors.PLUGIN_NOT_FOUND


@pytest.mark.asyncio
async def test_transaction_command_grpc_err(mock_get_transaction, mock_client_transaction_fail, make_plugin):
    """Get a TransactionResponse when the plugin exists but cant communicate with it."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction('foo')
    except errors.SynseError as e:
        assert e.error_id == errors.FAILED_TRANSACTION_COMMAND


@pytest.mark.asyncio
async def test_transaction_command_no_transaction(clear_caches):
    """Get a transaction that doesn't exist in the cache."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction('nonexistent')
    except errors.SynseError as e:
        assert e.error_id == errors.TRANSACTION_NOT_FOUND


@pytest.mark.asyncio
async def test_transaction_command(mock_get_transaction, mock_client_transaction, make_plugin):
    """Get a TransactionResponse when the plugin exists."""

    resp = await check_transaction('foo')

    assert isinstance(resp, TransactionResponse)
    assert resp.data == {
        'id': 'foo',
        'context': {
            'action': 'foo',
            'raw': [b'bar']
        },
        'state': 'ok',
        'status': 'done',
        'created': 'october',
        'updated': 'november',
        'message': ''
    }


@pytest.mark.asyncio
async def test_transaction_none(clear_caches):
    """Pass None to the transaction command when no transactions exist."""

    resp = await check_transaction(None)
    assert isinstance(resp, TransactionListResponse)
    assert len(resp.data) == 0


@pytest.mark.asyncio
async def test_transaction_none2(clear_caches):
    """Pass None to the transaction command when transactions exist."""

    ok = await synse.cache.add_transaction('abc123', {'some': 'ctx'}, 'test-plugin')
    assert ok

    resp = await check_transaction(None)
    assert isinstance(resp, TransactionListResponse)
    assert len(resp.data) == 1
    assert 'abc123' in resp.data
