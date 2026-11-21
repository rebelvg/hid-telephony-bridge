#!/usr/bin/env python3
"""Enable USB telephony mode so the Shure MV7+ can handle its own mute."""

import argparse
import errno
import logging
import signal
import time
from pathlib import Path
from select import POLLERR, POLLHUP, POLLIN, POLLNVAL, poll

DEFAULT_VID = "14ed"
DEFAULT_PID = "1019"
OFF_HOOK_ON = b"\x05\x01"
OFF_HOOK_OFF = b"\x05\x00"
PHONE_MUTE_REPORT = 0x04
PHONE_MUTE_BIT = 0x02
DEVICE_GONE_ERRORS = (errno.ENOENT, errno.ENODEV, errno.ENXIO, errno.EIO)

log = logging.getLogger("hid-telephony-bridge")


def find_hidraw_device(vid, pid):
    hid_id = f"HID_ID=0003:{vid:08X}:{pid:08X}"
    for entry in sorted(Path("/sys/class/hidraw").glob("hidraw*")):
        try:
            properties = (entry / "device/uevent").read_text(errors="replace").splitlines()
        except OSError:
            continue
        if hid_id in properties:
            return Path("/dev") / entry.name
    return None


def monitor_device(device):
    """Keep telephony active until the device disconnects or the daemon stops."""
    try:
        device.write(OFF_HOOK_ON)
        log.info("Off-Hook ON")
        events = poll()
        events.register(device, POLLIN)
        while True:
            for _, event in events.poll():
                if event & (POLLERR | POLLHUP | POLLNVAL):
                    return
                if event & POLLIN:
                    report = device.read(64)
                    if not report:
                        return
                    if (
                        len(report) >= 2
                        and report[0] == PHONE_MUTE_REPORT
                        and report[1] & PHONE_MUTE_BIT
                    ):
                        log.debug("Mute button pressed")
    finally:
        try:
            device.write(OFF_HOOK_OFF)
            log.info("Off-Hook OFF")
        except OSError as error:
            if error.errno not in DEVICE_GONE_ERRORS:
                log.warning("Could not turn Off-Hook off: %s", error)


def run(device_path, vid, pid):
    delay = 2
    while True:
        path = device_path or find_hidraw_device(vid, pid)
        if path is not None:
            try:
                with open(path, "r+b", buffering=0) as device:
                    log.info("Opened %s", path)
                    device_path = None
                    delay = 2
                    monitor_device(device)
                log.info("Device disconnected")
            except PermissionError:
                log.warning(
                    "Permission denied: %s. Check the udev rule and the active local session.",
                    path,
                )
            except OSError as error:
                if error.errno not in DEVICE_GONE_ERRORS:
                    raise
                log.debug("%s: %s", path, error)
        log.debug("Waiting for USB device %04x:%04x", vid, pid)
        time.sleep(delay)
        delay = min(delay * 1.5, 30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-d", "--device", help="hidraw path for the first connection")
    parser.add_argument("--vid", default=DEFAULT_VID, help="USB vendor ID in hex (default: %(default)s)")
    parser.add_argument("--pid", default=DEFAULT_PID, help="USB product ID in hex (default: %(default)s)")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Log mute button presses and device retries",
    )
    args = parser.parse_args()
    try:
        vid, pid = int(args.vid, 16), int(args.pid, 16)
        if not (0 <= vid <= 0xFFFF and 0 <= pid <= 0xFFFF):
            raise ValueError
    except ValueError:
        parser.error("--vid and --pid must be 16-bit hexadecimal USB IDs")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(name)s: %(message)s",
    )

    def stop(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        run(args.device, vid, pid)
    except KeyboardInterrupt:
        return 0
    except OSError as error:
        log.error("%s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
