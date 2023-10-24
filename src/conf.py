# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from pathlib import Path
import sys

sys.path.append(f"{Path('.').resolve()}")

project = "Mend Mental Health Therapy"
copyright = "2022-Present, Jen Mabey"
author = "Jen Mabey"

html_theme_options = {
    "project_subtitle": "You're good at helping others. It’s time to get good help for yourself!",
    # "catchphrase": "Live The Life You Choose Through Healing & Empowerment",
    "hero_button_text": "Get Started",
    "hero_href": "#how-to-begin",
    "author": "Jen Mabey, CMHC",
}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["my_custom_builder"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "tempo"
html_theme_path = ["."]
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_title = project
html_favicon = "_static/img/favicon.svg"
html_permalinks = False
html_scaled_image_link = False
html_use_index = False
html_copy_source = False


html5_doctype = True
language = "en"
encoding = "utf-8"
use_opensearch = False
