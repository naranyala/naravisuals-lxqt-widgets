cmake_minimum_required(VERSION 3.16)
project(naravisuals LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Core DBus)
find_package(lxqt REQUIRED)

add_library(naravisuals MODULE
    naravisuals-plugin.cpp
)

target_link_libraries(naravisuals PRIVATE
    Qt6::Widgets
    Qt6::Core
    lxqt
)

target_include_directories(naravisuals PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

install(TARGETS naravisuals
    LIBRARY DESTINATION lib/x86_64-linux-gnu/lxqt-panel
)

install(CODE "
    set(plugin_dir \$ENV{DESTDIR}/lib/x86_64-linux-gnu/lxqt-panel)
    set(widgets system-monitor weather quick-notes clipboard-manager pomodoro network-monitor tray-enhanced media-player battery)
    foreach(widget \${widgets})
        file(CREATE_LINK libnaravisuals.so libnaravisuals-\${widget}.so SYMBOLIC)
    endforeach()
")

install(DIRECTORY ../desktop-panel/
    DESTINATION share/lxqt/lxqt-panel
    FILES_MATCHING PATTERN "*.desktop"
)
