"""Setup script for the isnad2network package."""

from setuptools import setup, find_packages

setup(
    name="isnad2network",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
)
