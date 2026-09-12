"""Accepted translation fields and localized guide filename syntax.

The inspected frontend reads categories from main.nodeCategories and search
aliases from schemas. Accepting those node fields does not make them active.
"""

NODE_TEXT_FIELDS = {"display_name", "description", "category"}
NODE_GROUP_FIELDS = {"inputs", "outputs", "search_aliases"}
INPUT_LABEL_FIELDS = {"tooltip", "placeholder", "options"}
OUTPUT_LABEL_FIELDS = {"tooltip"}

GUIDE_LOCALE_PATTERN = r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*"
