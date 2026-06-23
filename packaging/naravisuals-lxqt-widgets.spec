Name:           naravisuals-lxqt-widgets
Version:        2.0.0
Release:        1%{?dist}
Summary:        Advanced panel widgets and theme manager for LXQt desktop
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
lightweight LXQt desktop. Includes system monitoring widgets, theme manager,
panel configuration, desktop entry management, and SDDM login manager.

Features:
- System Monitor, Network, Battery, Weather widgets
- Theme Manager (Labwc, KWin, LXQt themes, colors, fonts, icons)
- Panel Layout Manager (add/remove/reorder plugins)
- Desktop Entry Manager (browse/create/edit .desktop files)
- SDDM Display Manager theming

%prep
%setup -q

%build
cd native-plugin
mkdir -p build
cd build
%cmake ..
%make_build

cd ../..
%py3_build

%install
%py3_install
cd native-plugin/build
%make_install

# Systemd service
install -Dpm 644 packaging/naravisuals-daemon.service \
    %{buildroot}%{_userunitdir}/naravisuals-daemon.service

# Stock panel config
install -Dpm 644 packaging/stock-panel.conf \
    %{buildroot}%{_datadir}/naravisuals/stock-panel.conf

# Panel reset tool
install -Dpm 755 scripts/naravisuals-panel-reset \
    %{buildroot}%{_bindir}/naravisuals-panel-reset

# GUI launcher scripts (nv- prefix)
for app in nv-manager nv-manager-legacy nv-theme-store nv-desktop-manager nv-sddm-manager; do
    case "$app" in
        nv-manager)          mod="naravisuals.manager.control_center" ;;
        nv-manager-legacy)   mod="naravisuals.manager.app" ;;
        nv-theme-store)      mod="naravisuals.theme_manager.app" ;;
        nv-desktop-manager)  mod="naravisuals.desktop_manager.app" ;;
        nv-sddm-manager)     mod="naravisuals.sddm_manager.app" ;;
    esac
    cat > %{buildroot}%{_bindir}/$app << EOF
#!/usr/bin/env bash
exec python3 -m $mod "\$@"
EOF
    chmod 755 %{buildroot}%{_bindir}/$app
done

# Desktop files
install -Dpm 644 desktop/nv-manager.desktop \
    %{buildroot}%{_datadir}/applications/nv-manager.desktop
install -Dpm 644 desktop/nv-theme-store.desktop \
    %{buildroot}%{_datadir}/applications/nv-theme-store.desktop
install -Dpm 644 desktop/nv-desktop-manager.desktop \
    %{buildroot}%{_datadir}/applications/nv-desktop-manager.desktop
install -Dpm 644 desktop/nv-sddm-manager.desktop \
    %{buildroot}%{_datadir}/applications/nv-sddm-manager.desktop

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
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
%doc README.md TODOS.md

# Python packages
%{python3_sitelib}/naravisuals/
%{python3_sitelib}/%{name}-%{version}-py%{python3_version}.egg-info/

# GUI binaries (nv- prefix)
%{_bindir}/nv-manager
%{_bindir}/nv-manager-legacy
%{_bindir}/nv-theme-store
%{_bindir}/nv-desktop-manager
%{_bindir}/nv-sddm-manager

# Utility binaries
%{_bindir}/naravisuals-panel-reset

# Native plugin
%{_libdir}/lxqt/lxqt-panel/*.so

# Systemd user service
%{_userunitdir}/naravisuals-daemon.service

# Data files
%{_datadir}/naravisuals/
%{_datadir}/applications/nv-*.desktop

%changelog
* Sun Jun 23 2026 NaraVisuals <naranyala@users.noreply.github.com> - 2.0.0-1
- Renamed GUI apps to nv- prefix
- Added Theme Manager (Labwc/KWin/LXQt/Panel/Colors)
- Added Desktop Entry Manager
- Added PyInstaller packaging support
- Added AppImage and Flatpak build support

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
