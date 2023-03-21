from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in salla/__init__.py
from salla import __version__ as version

setup(
	name="salla",
	version=version,
	description="Integrate store salla to erpnext",
	author="baha",
	author_email="baha@slnee.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
