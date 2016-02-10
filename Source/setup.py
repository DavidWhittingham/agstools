try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('agstools/_version.py') as fin: exec(fin)

packages = [
    "agstools",
    "agstools.arcpy",
    "agstools.arcpyext",
    "agstools.agsadmin",
]

setup(
    name = "agstools",
    version = __version__,
    packages = packages,

    #dependencies
    install_requires = ["agsadmin>=0.1.2"],

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
