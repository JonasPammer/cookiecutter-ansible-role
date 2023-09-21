"""
NOTE - This file is jinja2'd by cookiecutter before its being executed,
meaning code inside jinja2 delimiters (even in comments) are parsed/replaced
and may even contain code that executes/calls cookiecutter functions (e.g. `update`).
So please do not remove any comments like these as they actually do stuff.

---

{{ cookiecutter.update({"role_name": cookiecutter.role_name.lower().replace(' ', '_').replace('-', '_') }) }}
"""
from __future__ import annotations
from __future__ import print_function


role_name = "{{ cookiecutter.role_name }}"
project_slug = "{{ cookiecutter.project_slug }}"

assert (
    "{%raw%}{{{%endraw%}" not in project_slug
), "project_slug contains {%raw%}{{{%endraw%}! '{}'".format(project_slug)

assert (
    "{%raw%}{{{%endraw%}" not in role_name
), "role_name contains {%raw%}{{{%endraw%}! '{}'".format(role_name)


role_name_ = "{{ cookiecutter.role_name_ | default(None) }}"
if role_name_ != "":
    print(
        "NOTE: role_name_ can be removed from your .cruft.json file "
        "(See https://github.com/JonasPammer/cookiecutter-ansible-role/pull/40). "
        "'{}'".format(role_name_)
    )
