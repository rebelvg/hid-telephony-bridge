# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Python daemon that enables USB HID Telephony mode so the Shure MV7+ can handle its own mute. The daemon sends Off-Hook on connection, reads Phone Mute reports, and clears Off-Hook on shutdown. The mic handles the audio mute and LED.

## Running and testing

```bash
# Foreground test (Shure MV7+ by default)
python3 hid-telephony-bridge.py --verbose
python3 hid-telephony-bridge.py --device /dev/hidrawN --verbose

# Select a different device with compatible reports
python3 hid-telephony-bridge.py --vid 1234 --pid 5678 --verbose

# Install on the host
bash ./install.sh

# Service management
systemctl --user status hid-telephony-bridge.service
systemctl --user restart hid-telephony-bridge.service
journalctl --user -u hid-telephony-bridge.service -f
```

Python 3.8+ and its standard library are sufficient to run the bridge.

## USB and session details

- USB vendor and product IDs default to `14ed:1019`. The daemon matches the HID ID in sysfs and redetects the node after disconnects.
- Off-Hook output is report `0x05`. Phone Mute input is report `0x04`, with bit 1 set on press.
- `70-hid-telephony-bridge.rules` gives the active local user access via `uaccess`.
- `hid-telephony-bridge.service` is a systemd user service. The installer uses root only for system files and udev.
- `PKGBUILD` and `hid-telephony-bridge.install` define the Arch package.
