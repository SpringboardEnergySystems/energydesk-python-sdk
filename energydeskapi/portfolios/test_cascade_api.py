from unittest import mock

import pytest

from energydeskapi.portfolios.cascade_api import CascadeApi, CascadeApiError

PARAMS = {"contract_type": "FORWARD", "cascade_date": "2026-09-24", "trading_book_ids": [10],
          "period_from": "QUARTER", "market_place": "NASDAQ_OMX", "price_mode": "LAST_CLOSE"}
REPORT = {"simulation": True, "errors": [], "contracts": []}


def connection(post=None, get=None):
    conn = mock.Mock()
    conn.exec_post_url.return_value = post
    conn.exec_get_url.return_value = get
    return conn


def test_simulate_and_execute_post_the_params_untouched_and_return_the_report():
    for call, action in ((CascadeApi.simulate_cascade, "simulate"), (CascadeApi.execute_cascade, "execute")):
        conn = connection(post=(True, REPORT, 200, None))
        assert call(conn, PARAMS) == REPORT
        conn.exec_post_url.assert_called_once_with(f"/api/portfoliomanager/cascading/{action}/", payload=PARAMS)


def test_undo_sends_process_id_and_explicit_simulation_flag():
    conn = connection(post=(True, REPORT, 200, None))
    assert CascadeApi.undo_cascade(conn, 7, False) == REPORT
    conn.exec_post_url.assert_called_once_with("/api/portfoliomanager/cascading/undo/", payload={"process_id": 7, "simulation": False})


def test_list_processes_passes_only_given_filters():
    conn = connection(get=[{"id": 1}])
    assert CascadeApi.list_cascade_processes(conn) == [{"id": 1}]
    conn.exec_get_url.assert_called_with("/api/portfoliomanager/cascading/processes/", {})
    CascadeApi.list_cascade_processes(conn, trading_book=10, limit=5)
    conn.exec_get_url.assert_called_with("/api/portfoliomanager/cascading/processes/", {"trading_book": 10, "limit": 5})


def test_json_error_body_is_relayed_with_status_detail_and_body():
    body = '{"detail": "No simulation has been run with these parameters.", "fingerprint": "abc"}'
    with pytest.raises(CascadeApiError) as raised:
        CascadeApi.execute_cascade(connection(post=(False, None, 409, body)), PARAMS)
    assert raised.value.status_code == 409
    assert raised.value.detail == "No simulation has been run with these parameters."
    assert raised.value.body["fingerprint"] == "abc"


def test_aborted_execute_keeps_the_report_in_the_body():
    body = '{"detail": "aborted", "report": {"errors": ["XXXQ1-27 (book 1): boom"]}}'
    with pytest.raises(CascadeApiError) as raised:
        CascadeApi.execute_cascade(connection(post=(False, None, 409, body)), PARAMS)
    assert raised.value.body["report"]["errors"] == ["XXXQ1-27 (book 1): boom"]


def test_validation_error_body_that_is_a_field_dict_has_no_detail_key():
    body = '{"price_mode": ["not allowed"]}'
    with pytest.raises(CascadeApiError) as raised:
        CascadeApi.simulate_cascade(connection(post=(False, None, 400, body)), PARAMS)
    assert raised.value.status_code == 400
    assert raised.value.body == {"price_mode": ["not allowed"]}


def test_non_json_error_text_is_kept_as_detail():
    with pytest.raises(CascadeApiError) as raised:
        CascadeApi.undo_cascade(connection(post=(False, None, 404, "Cascade process not found")), 9, True)
    assert (raised.value.status_code, raised.value.detail, raised.value.body) == (404, "Cascade process not found", None)


def test_failed_list_raises():
    with pytest.raises(CascadeApiError):
        CascadeApi.list_cascade_processes(connection(get=None))
