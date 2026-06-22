# Maintainer: Your Name <youremail@domain.com>
pkgname=naravisuals-lxqt-widgets-git
pkgver=1.0.0
pkgrel=1
pkgdesc="Custom LXQt panel widgets written in Python/PyQt6"
arch=('x86_64')
url="https://github.com/naranyala/naravisuals-lxqt-widgets"
license=('GPL3')
depends=('python-pyqt6' 'python-psutil' 'python-requests' 'python-dbus' 'lxqt-panel')
makedepends=('git' 'cmake' 'lxqt-build-tools')
provides=('naravisuals-lxqt-widgets')
conflicts=('naravisuals-lxqt-widgets')
source=("git+https://github.com/naranyala/naravisuals-lxqt-widgets.git")
sha256sums=('SKIP')

build() {
  cd "$srcdir/${pkgname%-git}"
  
  # Build native plugin
  mkdir -p native-plugin/build
  cd native-plugin/build
  cmake .. -DCMAKE_INSTALL_PREFIX=/usr
  make
}

package() {
  cd "$srcdir/${pkgname%-git}"
  
  # Install native plugin
  cd native-plugin/build
  make DESTDIR="$pkgdir/" install
  cd ../..
  
  # Install Python package
  python setup.py install --root="$pkgdir/" --optimize=1
  
  # Install desktop files
  install -dm755 "$pkgdir/usr/share/applications"
  install -m644 desktop/*.desktop "$pkgdir/usr/share/applications/"
}
