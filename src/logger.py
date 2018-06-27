import curses
import atexit
from datetime import datetime


class Logger():
    def __init__(self, *args, **kwargs):
        self._stdscr = curses.initscr()
        height, width = self._stdscr.getmaxyx()

        curses.start_color()
        curses.use_default_colors()

        self._initialize_log()
        atexit.register(curses.endwin)

    def _initialize_log(self):
        # Box hHaders
        DIVIDER = "---------------------------------------------"
        self._width = len(DIVIDER)

        TIME_ACTIVE = "Time Active:"
        TIME_HEALTY = "Time Healthy:"
        TIME_CRITICAL = "Time Critical:"

        HITS_TOTAL = "Hits (Total):"
        HITS_2_MIN = "Hits (Last Two Minutes):"

        DEFAULT_TIME = "0:00:00.00"

        # Set up summary
        self._stdscr.addstr(0, 0, "Summary")
        self._stdscr.addstr(1, 0, DIVIDER)
        self._stdscr.addstr(2, 0, TIME_ACTIVE)
        self._stdscr.addstr(3, 0, TIME_HEALTY)
        self._stdscr.addstr(4, 0, TIME_CRITICAL)
        self._stdscr.addstr(6, 0, HITS_TOTAL)
        self._stdscr.addstr(7, 0, HITS_2_MIN)

        # Set up alerts
        self._alerts_bottom = 11
        self._stdscr.addstr(self._alerts_bottom - 1, 0, "Alerts:")
        self._stdscr.addstr(self._alerts_bottom, 0, DIVIDER)

        self._top_sites_padding = 2

        self._stdscr.addstr(self._top_sites_padding + self._alerts_bottom, 0, "Top Sites by Hits (Updated every 10 s):")
        self._stdscr.addstr(self._top_sites_padding + self._alerts_bottom + 1, 0, DIVIDER)

        self._stdscr.addstr(3, self._width - len(DEFAULT_TIME), DEFAULT_TIME)
        self._stdscr.addstr(4, self._width - len(DEFAULT_TIME), DEFAULT_TIME)

        self._stdscr.refresh()

    def add_critical_status_alert(self, hits):
        alert = "High traffic generated an alert! Hits (Last 2 Min): {}, Triggered at {}".format(
            hits, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self._add_alert(alert)

    def add_healthy_status_alert(self, hits):
        alert = "Traffic returned to the expected threshold at {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self._add_alert(alert)

    def _add_alert(self, alert):
        self._stdscr.move(self._alerts_bottom + 1, 0)
        self._stdscr.insertln()
        self._stdscr.addstr(self._alerts_bottom + 1, 0, alert)
        self._stdscr.refresh()
        self._alerts_bottom += 1

    def update_timer(self, elapsed, healthy, critical):
        elapsed_str = str(elapsed)[0:10]
        start = self._width - len(elapsed_str)
        self._stdscr.addstr(2, start, elapsed_str)
        self._stdscr.refresh()

        self._update_time_healthy(healthy)
        self._update_time_critical(critical)

    def _update_time_healthy(self, elapsed):
        time = str(elapsed)[:10]
        start = self._width - len(time)
        self._stdscr.addstr(3, start, time)
        self._stdscr.refresh()

    def _update_time_critical(self, elapsed):
        time = str(elapsed)[:10]
        start = self._width - len(time)
        self._stdscr.addstr(4, start, time)
        self._stdscr.refresh()

    def update_hits(self, hits):
        # Clear the last 10 characters
        hits_str = str(hits)
        self._stdscr.addstr(6, self._width - len(hits_str), hits_str)
        self._stdscr.refresh()

    def update_hits_2_min(self, hits):
        # Clear the last 10 characters
        hits_str = str(hits)
        start_point = self._width - 2 * len(hits_str)
        self._stdscr.move(7, start_point)
        self._stdscr.clrtoeol()
        self._stdscr.addstr(7, self._width - len(hits_str), hits_str)
        self._stdscr.refresh()

    def update_top_sites(self, top_sites):
        self._clear_after_line(self._get_top_sites_start() + 1)
        for indx, val in enumerate(top_sites):
            self._stdscr.addstr(self._get_top_sites_start() + indx + 1, 0, str(val[0])[:self._width - 3])
            self._stdscr.addstr(self._get_top_sites_start() + indx + 1, self._width - len(str(val[1])), str(val[1]))
        self._stdscr.refresh()

    def _clear_after_line(self, line):
        self._stdscr.move(line, 0)
        self._stdscr.clrtobot()

    def _get_top_sites_start(self):
        return self._alerts_bottom + self._top_sites_padding + 1
