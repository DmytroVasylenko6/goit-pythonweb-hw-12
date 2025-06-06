# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("../src"))
print("------------------------", os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

project = "Contacts API"
copyright = "2025, Dmytro Vasylenko"
author = "Dmytro Vasylenko"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "nature"
html_static_path = ["_static"]
