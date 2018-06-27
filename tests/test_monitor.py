import pytest
import sys, os
from datetime import datetime
curr_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, curr_path + '/../src/')
from monitor import Monitor


@pytest.fixture
def empty_monitor():
    return DummyMonitor(**kwargs)


@pytest.fixture
def hits_added_monitor(empty_monitor):
    args = ("host.com", "/site/subsite")
    hits_to_add = hits_added_default
    for i in range(0, hits_to_add):
        empty_monitor.add(*args)
    return empty_monitor


# ------------TESTS---------------============================ #
def test_hits_added_monitor_is_valid(hits_added_monitor):
    simulate_time(hits_added_monitor, 5000)
    assert hits_added_monitor._hits == hits_added_default


def test_initial_hits(empty_monitor):
    assert empty_monitor._hits == 0


def test_initial_hits_2_min(empty_monitor):
    assert empty_monitor._hits_2_min == 0


def test_initial_status(empty_monitor):
    assert empty_monitor._status == "Healthy"


def test_add_hits(empty_monitor):
    hits_to_add = 50
    add_hits(empty_monitor, hits_to_add)
    simulate_time(empty_monitor, 5000)
    assert empty_monitor._hits == hits_to_add


def test_add_hits_2_min(empty_monitor):
    hits_to_add_2_min = 100
    add_hits(empty_monitor, hits_to_add_2_min)
    simulate_time(empty_monitor, 5000)
    assert empty_monitor._hits_2_min == hits_to_add_2_min


def test_flush_hits_2_min(hits_added_monitor):
    # Sim 2.5 Mins
    simulate_time(hits_added_monitor, 150000)
    assert hits_added_monitor._hits_2_min == 0


def test_critical_status(hits_added_monitor):
    simulate_time(hits_added_monitor, 5000)
    assert hits_added_monitor._status == "Critical"


def test_healthy_status(empty_monitor):
    add_hits(empty_monitor, 1)
    simulate_time(empty_monitor, 100)
    assert empty_monitor._status == "Healthy"


def test_status_recovery(hits_added_monitor):
    simulate_time(hits_added_monitor, 150000)
    assert hits_added_monitor._status == "Healthy"


def test_multiple_alert_recovery(empty_monitor):
    for hits, sim_time, expected_status in get_action_stream():
        add_hits(empty_monitor, hits)
        simulate_time(empty_monitor, sim_time)
        assert empty_monitor._status == expected_status


# ------------Test Helpers---------------- #
def simulate_time(monitor, sim_time):
    intervals = int(sim_time / monitor._refresh_freq)
    for i in range(0, intervals):
        monitor._process_queue()


def add_hits(monitor, hits):
    args = ("host.com", "/site/subsite")
    for i in range(0, hits):
        monitor.add(*args)


def get_action_stream():
    return (
        (1, 1000, "Healthy"),
        (100, 1000, "Critical"),
        (0, 1000, "Critical"),
        (0, 150000, "Healthy"),
        (5, 1000, "Healthy"),
        (10, 1000, "Critical"),
        (0, 150000, "Healthy")
    )


hits_added_default = 10000

critical_threshold = 10
kwargs = {"high_traffic_threshold": critical_threshold, "__test__": True}


class DummyMonitor(Monitor):
    def __init__(self, **kwargs):
        Monitor.__init__(self, **kwargs)
        self._logger = DummyLogger()


class DummyLogger():
    def __init__(self):
        none_func = lambda *args, **kwargs: None
        self.update_top_sites = none_func
        self.update_hits = none_func
        self.update_timer = none_func
        self.update_hits_2_min = none_func
        self.add_critical_status_alert = none_func
        self.add_healthy_status_alert = none_func
