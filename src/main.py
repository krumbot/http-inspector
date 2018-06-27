import argparse
from sniff import Sniffer

def main(**kwargs):
    sniffer = Sniffer(**kwargs)
    sniffer.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor HTTP Traffic")
    parser.add_argument("--critical-traffic", type=int)
    args = parser.parse_args()

    sniffer_args = {}

    if args.critical_traffic is not None:
        sniffer_args["high_traffic_threshold"] = args.critical_traffic
    main(**sniffer_args)
