from __future__ import annotations

from pathlib import Path

from setuptools import setup, find_packages


def parse_requirements(file: Path) -> list[str]:
    lines = file.read_text().splitlines()
    return [line.rstrip() for line in lines if line and not line.startswith("#")]


here = Path(__file__).parent.absolute()

requirements = parse_requirements(here / "requirements.txt")
test_requirements = parse_requirements(here / "requirements-test.txt")
long_description = (here / "README.rst").read_text()

setup(
    name="etl-entities",
    version_config={
        "template": "{tag}",
        "dev_template": "{tag}.dev{env:BUILD_ID:{ccount}}",
        "dirty_template": "{tag}",
        "version_file": here / "etl_entities" / "VERSION",
        "count_commits_from_version_file": True,
    },
    author="Volkov Dmitrii",
    description="ETL Entities lib",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.services.mts.ru/bigdata/platform/onetools/etl-entities",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    classifiers=[
        "Topic :: Software Development :: HWM lib",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_require=requirements,
    tests_require=test_requirements,
    extras_require={"test": test_requirements},
    setup_requires=["setuptools-git-versioning"],
    test_suite="tests",
    zip_safe=False,
)
