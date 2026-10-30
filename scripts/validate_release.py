"""Require a plain version tag matching both built distributions."""

import email
import os
import tarfile
import zipfile
from pathlib import Path

from packaging.version import Version


def validate(tag, directory):
    version = Version(tag)
    if tag.startswith("v") or str(version) != tag:
        raise ValueError("Use a canonical version tag without a leading v")
    wheels = list(directory.glob("*.whl"))
    sources = list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise ValueError("Expected exactly one wheel and one source distribution")
    with zipfile.ZipFile(wheels[0]) as wheel:
        metadata = [
            name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata) != 1:
            raise ValueError("Expected exactly one wheel metadata file")
        wheel_metadata = email.message_from_bytes(wheel.read(metadata[0]))
    with tarfile.open(sources[0], "r:gz") as source:
        metadata = [
            member
            for member in source.getmembers()
            if member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
        ]
        if len(metadata) != 1:
            raise ValueError("Expected exactly one source metadata file")
        source_metadata = email.message_from_bytes(
            source.extractfile(metadata[0]).read()
        )
    for metadata in (wheel_metadata, source_metadata):
        if metadata["Name"] != "zsm" or metadata["Version"] != tag:
            raise ValueError("Distribution name or version does not match release tag")
    return version.is_prerelease or version.is_devrelease


if __name__ == "__main__":
    prerelease = validate(os.environ["RELEASE_TAG"], Path("dist"))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write("prerelease=" + str(prerelease).lower() + "\n")
    print("Validated release " + os.environ["RELEASE_TAG"])
