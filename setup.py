from setuptools import setup, find_packages

setup(
    name="naravisuals-lxqt-widgets",
    version="1.0.0",
    description="Custom LXQt panel widgets written in Python/PyQt6",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5",
        "psutil>=5.8",
        "requests>=2.25",
        "dbus-python>=1.2",
        "notify2>=0.3",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "naravisuals-manager=naravisuals.panel_plugin:main",
            "naravisuals-widget=naravisuals.widgets.__main__:main",
        ]
    },
)
