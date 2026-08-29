from setuptools import setup


setup(
    name="ruff",
    version="0.16.4",
    packages=["ruff"],
    package_data={"ruff": ["_ruff_bin"]},
    entry_points={"console_scripts": ["ruff=ruff.cli:main"]},
)
