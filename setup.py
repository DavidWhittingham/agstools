from setuptools import setup, find_packages

with open("agstools/_version.py") as fin: exec(fin)
with open("requirements.txt") as fin: requirements = [s.strip() for s in fin.readlines()]
with open("README.rst") as fin: long_description = fin.read()

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    name = "agstools",
    version = __version__,
    packages = packages,

    #dependencies
    install_requires = requirements,

    #misc files to include
    package_data = {
        "": ["LICENSE"]
    },

    #automatic script creation
    entry_points = {
        "console_scripts": [
            "agstools = agstools:main"
        ]
    },

    #PyPI MetaData
    author = __author__,
    description = "ArcGIS Server 10.1+ Administrative Command-Line Tools",
    long_description = long_description,
    license = "BSD 3-Clause",
    keywords = "arcgis esri",
    url = "https://github.com/DavidWhittingham/agstools",
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7"
    ),

    zip_safe = True
)
