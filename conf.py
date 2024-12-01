import os
import sys

# Add multiple source directories to sys.path
sys.path.insert(0, os.path.abspath('/customer_service'))
sys.path.insert(0, os.path.abspath('/inventory_service'))
sys.path.insert(0, os.path.abspath('/sales_service'))
sys.path.insert(0, os.path.abspath('/reviews_service'))



# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = '435L final'
copyright = '2024, balaa and daaboul'
author = 'balaa and daaboul'
release = '1/12/24'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
