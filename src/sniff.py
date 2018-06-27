from scapy.all import sniff
from scapy_http import http
from monitor import Monitor
from threading import Thread


class Sniffer:
    def __init__(self, **kwargs):
        self._monitor = Monitor(**kwargs)

    # Start the monitor and the sniffer
    def start(self):
        self._monitor.start()
        sniff(filter="tcp and port 80", prn=self._read_packet)

    # Create a new thread to process each packet
    def _read_packet(self, packet):
        if packet.haslayer(http.HTTPRequest):
            layer = packet.getlayer(http.HTTPRequest)
            host = layer.fields["Host"].decode("UTF-8")
            path = layer.fields["Path"].decode("UTF-8")
            self._monitor.add(host, path)
            thread = Thread(target=self._monitor.add, args=(host, path))
            thread.start()
            thread.join()
