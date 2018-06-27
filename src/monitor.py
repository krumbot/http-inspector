from datetime import datetime, timedelta
from logger import Logger
import threading
import math


class Monitor():
    def __init__(self, **kwargs):
        if "high_traffic_threshold" in kwargs:
            self._high_traffic = kwargs["high_traffic_threshold"]
        else:
            self._high_traffic = 100

        self._refresh_freq = 500

        self._num_top_sites = 10

        self._critical_monitor_time = 120
        self._hits = 0
        self._hits_2_min = 0

        self._elapsed = timedelta(0)
        self._time_critical = timedelta(0)
        self._time_healthy = timedelta(0)

        self._alert_queue = [0] * self._critical_monitor_time * math.floor((1000 / self._refresh_freq))
        self._site_queue = []
        self._history = {}
        self._status = "Healthy"

        # No keyword arguments to logger at the moment, but this is where color options would be passed in
        if "__test__" not in kwargs:
            self._logger = Logger(**kwargs)

        # Critical and Recovered Alerts
        self._alerts = [0, 0]

    def add(self, host, path):
        trim_path = path.split("/")[1].split("?")[0]
        site = "{}/{}".format(host, trim_path)
        self._site_queue.append(site)

    def start(self):
        self._start_time = datetime.now()
        self._alert_interval()
        self._top_sites_interval()

    def _alert_interval(self):
        def wrapper():
            self._alert_interval()
            self._process_queue()

        self._alert_timer = threading.Timer(self._refresh_freq / 1000, wrapper)
        self._alert_timer.start()

    def _top_sites_interval(self):
        def wrapper():
                self._top_sites_interval()
                self._update_top_sites()
        self._top_sites_timer = threading.Timer(10.0, wrapper)
        self._top_sites_timer.start()

    def _update_top_sites(self):
        top_sites = [(key, self._history[key]) for key in sorted(
            self._history, key=self._history.get, reverse=True)][:self._num_top_sites]
        self._logger.update_top_sites(top_sites)

    def _update_hits(self, hits):
        self._hits += hits
        self._logger.update_hits(self._hits)

    def _process_queue(self):
        self._update_time()
        hits = len(self._site_queue)
        self._alert_queue.insert(0, hits)
        self._alert_queue.pop()
        self._update_sites()
        self._update_hits(hits)
        self._update_alert_status()

    def _update_time(self):
        elapsed = datetime.now() - self._start_time
        change = elapsed - self._elapsed
        self._update_status_times(change)
        self._elapsed = elapsed
        self._logger.update_timer(self._elapsed, self._time_healthy, self._time_critical)

    def _update_status_times(self, change):
        if self._status == "Healthy":
            self._time_healthy += change
        else:
            self._time_critical += change

    def _update_sites(self):
        for site in self._site_queue:
            if site not in self._history:
                self._history[site] = 1
            else:
                self._history[site] += 1
        self._site_queue = []

    def _update_alert_status(self):
        hits = sum(self._alert_queue)
        self._hits_2_min = hits
        self._logger.update_hits_2_min(hits)
        if hits >= self._high_traffic:
            if self._status == "Healthy":
                self._logger.add_critical_status_alert(hits)
                self._status = "Critical"
                self._alerts[0] += 1
        else:
            if self._status == "Critical":
                self._logger.add_healthy_status_alert(hits)
                self._status = "Healthy"
                self._alerts[1] += 1
