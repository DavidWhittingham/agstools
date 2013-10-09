from ez_setup import use_setuptools
use_setuptools()
    
import agstools

from setuptools import setup, find_packages
setup(
    name = "agstools",
    version = agstools.__version__,
    packages = find_packages(),
    
    #dependencies
    install_requires = ["agsadmin"],
    
    #misc files to include
    package_data = {
        "": ["license.txt", "authors.txt"]
    },

    #automatic script creation
    entry_points = {
        "console_scripts": [
            "agstools = agstools.agstools:main"
        ]
    },
    
    #PyPI MetaData
    author = agstools.__author__,
    description = "ArcGIS Server 10.1+ Administrative Command-Line Tools",
    license = "BSD 3-Clause",
    keywords = "arcgis esri",
    
    zip_safe = True
)