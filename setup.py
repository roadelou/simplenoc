#!/usr/bin/env python3

################################### METADATA ###################################

# Contributors: roadelou
# Contacts: 
# Creation Date: 2021-01-21
# Language: Python3

################################### IMPORTS ####################################

# Standard library 
from setuptools import setup    # Used to describe the python package.


# External imports 
# Your imports from other packages go here 


# Internal imports 
# Your imports within this package go here 

################################### CLASSES ####################################

# Your classes go here 

################################## FUNCTIONS ###################################

def main():
    """
    Calls the setup function and defines the python package.
    """
    # Calling the setup function with the right arguments.
    setup(
        name="simplenoc",
        version="0.0.1",
        author="roadelou",
        author_email="tableau.roche@gmail.com",
        packages=["simplenoc"],   # Non-recursive list of source directories.
        license="GPL3",
        python_requires=">=3.6",
    )

##################################### MAIN #####################################

if __name__ == "__main__":
    # Calling the package creation function.
    main()

##################################### EOF ######################################
