from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in thirvusoft_bpm/__init__.py
from thirvusoft_bpm import __version__ as version

setup(
	name="thirvusoft_bpm",
	version=version,
	description="BPM",
	author="BPM",
	author_email="thirvusoft@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
