# Contributing

Thanks for helping keep the batteries in. This guide covers how to propose a change
and the Ansible coding standards every YAML file and playbook in this repo follows.

## Proposing a change

| I want to... | Edit |
|---|---|
| Add a collection that isn't in the `ansible` package | [`extra-collections.txt`](extra-collections.txt), then run `scripts/update-requirements.py` |
| Drop a collection from the image | [`excluded-collections.txt`](excluded-collections.txt), then run `scripts/update-requirements.py` |
| Add a Python library a module needs | [`requirements.txt`](requirements.txt), with a comment naming the module/plugin |
| Add a system package | [`bindep.txt`](bindep.txt), with `[platform:rpm]` (add `compile` if it's only needed to build wheels) |
| Change the base image or build steps | [`execution-environment.yml`](execution-environment.yml) |

Never hand-edit [`requirements.yml`](requirements.yml) or the collection table in the README: both are generated.

### Before opening a pull request

```sh
pip install ansible-builder ansible-lint pre-commit
pre-commit run --all-files                         # yamllint + ansible-lint + hygiene
ansible-builder build --tag ansible_aio_ee:dev -v 3
docker run --rm -v "$PWD/tests:/tests:ro" ansible_aio_ee:dev \
  ansible-playbook /tests/smoke.yml
```

CI runs the same lint, build and [smoke test](tests/smoke.yml) on every pull request (amd64 only).

## Ansible coding standards

These follow the [Ansible community "good practices"](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html),
the [Red Hat Communities of Practice Automation Good Practices](https://redhat-cop.github.io/automation-good-practices/)
and ansible-lint's **`production`** profile, which [`.ansible-lint`](.ansible-lint) enforces.

### YAML

- Start every YAML file with `---`. Indent two spaces, never tabs; end with a newline.
- Use `true` / `false` for booleans, never `yes`, `no`, `True` or `on`.
- Keep lines at 160 characters or less. Use `>-` folded scalars for long commands and messages.
- Quote strings that contain `{{ }}`, `:` or start with special characters. Otherwise prefer unquoted scalars.
- Write dictionaries in block style. Short inline maps are OK in generated files only (`requirements.yml`).

### Playbooks and tasks

- **Name everything.** Every play, task and block gets a `name:` in sentence case that says *what* it achieves: `Install web server packages`, not `yum`.
- **Use FQCNs** for every module, filter and lookup: `ansible.builtin.copy`, `community.general.json_query`. Never use short names.
- **Use the native YAML syntax** for module arguments, never `key=value` strings.
- **Keep tasks idempotent.** Prefer purpose-built modules over `command`/`shell`. When you must use them, set `changed_when` (and `creates`/`removes` where possible), and use `ansible.builtin.command` unless you need shell features.
- **Don't hide failures.** Avoid `ignore_errors`. Use `failed_when` or `block`/`rescue`. If a failure *is* the expected outcome, add a `# noqa: ignore-errors` with the reason.
- **Use `become` only where it's needed**, at task or block level rather than the whole play.
- Always set `mode:` on files and templates you create, and use quoted octal (`mode: "0644"`).
- Don't write `when:` with `{{ }}`. Conditions are already Jinja expressions.
- Prefer `loop:` over `with_*`, and `ansible.builtin.include_tasks` / `import_tasks` over `include`.

### Variables

- Name variables in `snake_case`. Role variables are prefixed with the role name (`webserver_port`), and registered variables carry a prefix too (`smoke_ldap`).
- Never commit secrets. Use Ansible Vault, AWX credentials or a secrets manager lookup such as `community.hashi_vault`, and mark sensitive tasks `no_log: true`.
- Keep defaults in `defaults/main.yml`. Use `vars/` only for values users shouldn't override.

### Roles and collections

- One purpose per role, with `meta/argument_specs.yml` describing its inputs.
- Reference role content by FQCN when it lives in a collection.
- Pin collection versions in `requirements.yml` for anything you ship.

### Python (scripts/)

- Python 3.9+, standard library only, so scripts run on a bare CI runner.
- Follow PEP 8 with four-space indents. Keep a module docstring explaining usage.

## Commits

Write short, imperative commit subjects (`Add python-ldap for ldap_search`) and reference
issues where relevant (`Fixes #7`). By contributing you agree your changes are released
under the repository's [MIT license](LICENSE).
