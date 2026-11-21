# Maintainer: Stefan Mayer-Popp <stefan@mayer-popp.de>
pkgname=hid-telephony-bridge
pkgver=0.1.2
pkgrel=1
pkgdesc="Enable USB HID Telephony hardware mute on Linux (default: Shure MV7+)"
arch=('any')
url="https://github.com/fuxx/hid-telephony-bridge"
license=('GPL-3.0-only')
depends=('python')
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')
install=hid-telephony-bridge.install

_source_dir="$pkgname-$pkgver"
if [[ ${HID_TELEPHONY_BRIDGE_LOCAL_BUILD:-0} == 1 ]]; then
    source=(
        hid-telephony-bridge.py
        70-hid-telephony-bridge.rules
        hid-telephony-bridge.service
        LICENSE
        README.md
    )
    sha256sums=('SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP')
    _source_dir=.
fi

package() {
    cd "$srcdir/$_source_dir"
    install -Dm755 hid-telephony-bridge.py "$pkgdir/usr/bin/hid-telephony-bridge"
    install -Dm644 70-hid-telephony-bridge.rules "$pkgdir/usr/lib/udev/rules.d/70-hid-telephony-bridge.rules"
    install -Dm644 hid-telephony-bridge.service "$pkgdir/usr/lib/systemd/user/hid-telephony-bridge.service"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
