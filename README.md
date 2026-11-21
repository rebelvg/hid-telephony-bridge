# hid-telephony-bridge

Enables USB telephony mode so the **Shure MV7+** can mute itself promptly when you tap its LED bar. The daemon sends Off-Hook (report `0x05`), listens for mute button presses (report `0x04`), and turns Off-Hook off when stopped. The mic controls its own audio and mute LED. The daemon reconnects when you unplug and replug the mic.

## Install on Arch

### Build a package from this checkout

With Arch's base-devel installed, run this as your regular user from the checkout:

```bash
HID_TELEPHONY_BRIDGE_LOCAL_BUILD=1 makepkg -si
```

This builds the package from the files in the checkout and installs it with pacman. Replug the MV7+ to apply the udev rule, then start the user service:

```bash
systemctl --user enable --now hid-telephony-bridge.service
```

### Install directly

Run from this checkout as your regular user in an active local session:

```bash
bash ./install.sh
systemctl --user status hid-telephony-bridge.service
```

The installer uses `sudo` to copy the script and service and install a udev rule for the MV7+ (USB ID `14ed:1019`). The rule grants the active local user access to the mic's `hidraw` interface. The service runs as your user and starts at login. The bridge itself requires only Python 3.8+ and its standard library.

Make a local recording and tap mute, unmute, and mute again to check when the audio cuts out.

### Arch Linux (AUR)

For tagged releases, install through the AUR and enable the user service:

```bash
yay -S hid-telephony-bridge
systemctl --user enable --now hid-telephony-bridge.service
```

Replug the mic if the rule has just been installed and the service reports a permission error. To uninstall the package, stop the service first:

```bash
systemctl --user disable --now hid-telephony-bridge.service
yay -Rns hid-telephony-bridge
```

### Upgrade from a previous source install

If you installed the old rule at `/etc/udev/rules.d/99-hid-telephony-bridge.rules`, remove that legacy rule and replug the mic after installing the new version. Remove `--auto-offhook` or `--hid-only` from any existing command or systemd drop-in. Hardware mute is now the default.

## Foreground test

Stop the service if it is running, then run the bridge from the checkout:

```bash
python3 hid-telephony-bridge.py --verbose
```

Look for `Off-Hook ON` and `Mute button pressed`. Press `Ctrl+C` to stop. Use `--device /dev/hidrawN` to select a particular node for the first connection. The device needs read/write access for the handshake.

```bash
journalctl --user -u hid-telephony-bridge.service -f
systemctl --user disable --now hid-telephony-bridge.service
```

The first command follows the service log. The second stops the service and disables it at login.

## Other devices

Some microphones may support the same Off-Hook and Phone Mute reports. Hardware mute in this mode has been tested on the MV7+.

1. Use `lsusb` to find the device's vendor and product IDs.
2. Copy [the MV7+ udev rule](70-hid-telephony-bridge.rules) to `/etc/udev/rules.d/70-my-telephony-mic.rules` and replace the IDs. Reload the rules with `sudo udevadm control --reload-rules`, then replug the mic.
3. Run `systemctl --user edit hid-telephony-bridge.service` and add the following, substituting the IDs:

   ```ini
   [Service]
   ExecStart=
   ExecStart=/usr/bin/hid-telephony-bridge --vid XXXX --pid XXXX
   ```

   Restart the user service after saving.

## Releasing / AUR publishing

Releases use a two-step process to prevent supply chain attacks — CI builds but never pushes to AUR. Only a local, manually verified push can update the AUR package.

### 1. Tag and push

```bash
git tag v0.1.0
git push origin main --tags
```

This triggers the CI workflow (`.github/workflows/build-package.yml`) which:
- Builds the package in a clean Arch Linux container
- Computes SHA256 checksums of the source tarball, PKGBUILD, and `.SRCINFO`
- Uploads everything as a build artifact (PKGBUILD, .SRCINFO, checksums, .pkg.tar.zst)

### 2. Verify and push to AUR locally

Download `checksums.txt` from the GitHub Actions artifact, then:

```bash
./aur-push.sh v0.1.0
```

The script will:
- Download the source tarball and compute its SHA256 locally
- Compare against the CI checksum — **aborts on mismatch**
- Show the PKGBUILD and .SRCINFO for review
- Ask for confirmation before pushing to the AUR git repo

This ensures the tarball GitHub serves hasn't been tampered with between CI build and AUR publish. No secrets or SSH keys are stored in GitHub.

## License

GPL-3.0 — see [LICENSE](LICENSE)
