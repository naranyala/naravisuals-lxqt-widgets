Name:           naravisuals-lxqt-widgets
Version:        2.0.0
Release:        1%{?dist}
Summary:        Advanced panel widgets for LXQt desktop environment
License:        GPLv3+
URL:            https://github.com/naranyala/naravisuals-lxqt-widgets
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  cmake
BuildRequires:  lxqt-build-tools-devel

Requires:       python3 >= 3.10
Requires:       python3-pyqt6 >= 6.5
Requires:       python3-psutil >= 5.8
Requires:       python3-requests >= 2.25
Requires:       python3-dbus-python >= 1.2
Requires:       python3-notify2 >= 0.3
Requires:       lxqt-panel
Requires:       hicolor-icon-theme

%description
NaraVisuals provides advanced customization and extended functionality to the 
lightweight LXQt desktop. It integrates a native C++ panel plugin with a 
feature-rich Python/PyQt6 daemon, allowing complex UI elements to be embedded 
directly into the LXQt panel.

Features include system monitoring, weather widgets, productivity tools, 
clipboard management, and more.

%prep
%setup -q

%build
# Build native plugin
cd native-plugin
mkdir -p build
cd build
%cmake ..
%make_build

# Build Python package
cd ../..
%py3_build

%install
%py3_install

# Install native plugin
cd native-plugin/build
%make_install

# Install systemd service
install -Dpm 644 packaging/naravisuals-daemon.service \
    %{buildroot}%{_userunitdir}/naravisuals-daemon.service

# Install D-Bus service
install -Dpm 644 packaging/org.naravisuals.Daemon.service \
    %{buildroot}%{_datadir}/dbus-1/services/org.naravisuals.Daemon.service

# Install stock panel config
install -Dpm 644 packaging/stock-panel.conf \
    %{buildroot}%{_datadir}/naravisuals/stock-panel.conf

# Install desktop files
install -Dpm 644 desktop/naravisuals-manager.desktop \
    %{buildroot}%{_datadir}/applications/naravisuals-manager.desktop

# Install panel reset tool
install -Dpm 755 scripts/naravisuals-panel-reset \
    %{buildroot}%{_bindir}/naravisuals-panel-reset

# Create symlinks for widget launchers
for widget in system-monitor weather quick-notes clipboard-manager pomodoro \
              network-monitor tray-enhanced media-player battery; do
    ln -s naravisuals-widget %{buildroot}%{_bindir}/naravisuals-${widget}
done

%post
# Update icon cache
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

# Reload D-Bus
/usr/bin/dbus-send --session --type=method_call --dest=org.freedesktop.DBus \
    /org/freedesktop/DBus org.freedesktop.DBus.ReloadConfig || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%license LICENSE
%doc README.md TODOS.md WIDGET_EVALUATION.md

# Python packages
%{python3_sitelib}/naravisuals/
%{python3_sitelib}/%{name}-%{version}-py%{python3_version}.egg-info/

# Binaries
%{_bindir}/naravisuals-manager
%{_bindir}/naravisuals-daemon
%{_bindir}/naravisuals-widget
%{_bindir}/naravisuals-panel-reset
%{_bindir}/naravisuals-*

# Native plugin
%{_libdir}/lxqt/lxqt-panel/*.so

# Systemd user service
%{_userunitdir}/naravisuals-daemon.service

# D-Bus service
%{_datadir}/dbus-1/services/org.naravisuals.Daemon.service

# Data files
%{_datadir}/naravisuals/
%{_datadir}/applications/naravisuals-*.desktop
%{_datadir}/icons/hicolor/

%changelog
* Sat Jun 22 2026 NaraVisuals <naranyala@users.noreply.github.com> - 2.0.0-1
- D-Bus IPC architecture for Wayland support
- Single daemon process for all widgets
- Panel reset functionality
- RPM packaging for Fedora/RHEL

* Mon Jun 15 2026 NaraVisuals <naranyala@users.noreply.github.com> - 1.0.0-1
- Initial release
- 13 widgets: System Monitor, Weather, Pomodoro, etc.
- Native C++ panel plugin
- PyQt6 GUI manager
