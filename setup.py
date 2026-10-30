from pathlib import Path

import setuptools


setuptools.setup(
    name="zsm",
    version="1.0",
    keywords="zfs snapshots freebsd linux",
    description="ZFS Snapshot Manager",
    long_description=Path(__file__).with_name("README.rst").read_text(),
    long_description_content_type="text/x-rst",
    project_urls={
        "Documentation": "https://github.com/lots0logs/zsm/tree/main/docs",
        "Source": "https://github.com/lots0logs/zsm",
    },
    license="BSD-2-Clause",
    author="Mattias Lindvall",
    author_email="mattias.lindvall@gmail.com",
    package_dir={"": "src"},
    packages=["zsm"],
    python_requires=">=3.10",
    install_requires=[
        "click >= 8.1, < 9",
        "pid ~= 3.0.4",
        "pyyaml >= 6, < 7",
        "marshmallow >= 3.20, < 4",
    ],
    extras_require={
        "test": [
            "pytest >= 8, < 10",
            "pytest-cov >= 5, < 8",
            "flake8 >= 7, < 8",
            "flake8-bugbear >= 24, < 27",
            "black == 24.10.0",
            "isort >= 5.13, < 7",
            "invoke >= 2, < 3",
            "tox >= 4, < 5",
            "freezegun >= 1.5, < 2",
        ],
        "build": [
            "build >= 1, < 2",
            "twine >= 6, < 7",
        ],
    },
    entry_points={"console_scripts": ["zsm = zsm.cli:cli"]},
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        # "Development Status :: 6 - Mature",
        # "Development Status :: 7 - Inactive",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Filesystems",
    ],
)
