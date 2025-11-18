# CLAUDE.md - cookiecutter-ansible-role

## Project Overview

This is a **Cookiecutter template** for creating production-ready Ansible Roles. It generates complete role scaffolding with testing infrastructure, CI/CD pipelines, and development tooling pre-configured.

**Two-Layer Architecture:**
1. **Template Layer** (`/` root): The cookiecutter template itself that you develop/maintain
2. **Generated Layer** (`{{ cookiecutter.project_slug }}/`): What users receive when they use this template

## Core Architecture Patterns

### Variable Precedence Strategy

The template implements a sophisticated OS-specific variable pattern to overcome Ansible's variable precedence limitations. This is the **most important architectural pattern** to understand:

```yaml
# In vars/main.yml (high precedence, but still overridable via lazy evaluation)
_rolename__somevar:
  Debian: "value1"
  Debian_10: "value2"
  RedHat: "value3"

rolename__somevar: "{{
  _rolename__somevar[ansible_distribution ~ '_' ~ ansible_distribution_major_version]|default(
  _rolename__somevar[ansible_os_family ~ '_' ~ ansible_distribution_major_version])|default(
  _rolename__somevar[ansible_distribution])|default(
  _rolename__somevar[ansible_os_family])|default(
  _rolename__somevar['default']) }}"
```

**Why:** Allows OS-specific values without creating separate files per distribution, while remaining overridable despite being in `vars/` (high precedence). The lazy evaluation with Jinja2 allows playbook-level overrides.

**Naming Conventions:**
- `defaults/`: `rolename_varname` (single underscore)
- `vars/`: `rolename__varname` (double underscore)
- Registered variables: `rolename__register_modulename_varname`

### Pre-Generation Hook

`hooks/pre_gen_project.py` validates inputs before generation:
- Normalizes role names (lowercase, underscores)
- Ensures no Jinja2 syntax remains in critical variables
- Provides migration notes for cruft updates

## Template Development Commands

### Creating a Role from Template

```bash
# Install cruft (allows keeping roles updated with template changes)
python3 -m pip install cruft

# Generate a new role
cruft create https://github.com/JonasPammer/cookiecutter-ansible-role.git

# Update existing role with template changes
cruft update
```

### Testing the Template Itself

The template has its own CI workflow (`.github/workflows/ci.yml`) that tests template generation:

```bash
# Test template generation with example config
cookiecutter . --config-file .github/cookiecutter-example.yml --no-input
```

## Generated Role Development

When working **inside** a generated role:

### Setup Development Environment

```bash
# Install development dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Testing Commands

```bash
# Run all tests (linting + molecule tests across all Ansible versions)
tox

# Run tests for specific Ansible version
tox -e py3-ansible-9

# Run tests on specific distribution
MOLECULE_DISTRO=ubuntu2204 tox

# Run tests with specific Ansible version and distribution
MOLECULE_DISTRO=rockylinux9 tox -e py3-ansible-8

# Keep container running after test failure for debugging
MOLECULE_DESTROY=never MOLECULE_DISTRO=ubuntu2204 tox -e py3-ansible-9

# Show installed package versions (useful for debugging)
CI=true tox
```

**Supported Distributions:**
- `ubuntu2004`, `ubuntu2204`
- `debian11`, `debian12`
- `rockylinux8`, `rockylinux9`
- `fedora39`

**Supported Ansible Versions:**
- `ansible-6` (core 2.13)
- `ansible-7` (core 2.14)
- `ansible-8` (core 2.15)
- `ansible-9` (core 2.16)

### Debugging Failed Molecule Tests

```bash
# 1. Run with MOLECULE_DESTROY=never
MOLECULE_DESTROY=never MOLECULE_DISTRO=ubuntu2204 tox -e py3-ansible-9

# 2. Find container name
docker ps

# 3. Enter container
docker exec -it <container-id> /bin/bash

# 4. Debug files are available at:
# /var/tmp/vars.yml (contains hostvars)
# /var/tmp/environment.yml

# 5. Clean up when done
docker stop <container-id>
docker container rm <container-id>
```

### Linting Commands

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# YAML linting only
yamllint .

# Ansible linting only
ansible-lint
```

### Publishing Commands

```bash
# Release to Ansible Galaxy (requires GALAXY_API_KEY secret in GitHub)
# Triggered automatically on git tag push via .github/workflows/release-to-galaxy.yml
git tag 1.0.0
git push origin 1.0.0
```

## Testing Infrastructure

### Molecule Test Phases

1. **Prepare** (`molecule/resources/prepare.yml`): Bootstrap environment with `jonaspammer.bootstrap` role
2. **Converge** (`molecule/default/converge.yml`): Apply the role to test instance
3. **Verify** (`molecule/default/verify.yml`): Validate role execution results
4. **Debug** (`molecule/resources/debug.yml`): Collect system information for CI artifacts

### Multi-Dimensional Testing Matrix

Generated roles test across:
- **7 distributions** (Ubuntu, Debian, Rocky Linux, Fedora)
- **4 Ansible versions** (6, 7, 8, 9)
- Docker-based with systemd-enabled images (`geerlingguy/docker-*-ansible`)

### CI/CD Workflows (Generated Roles)

**`.github/workflows/ci.yml`** - Main testing pipeline:
- Runs `yamllint` on all YAML files
- Executes Molecule tests across distribution matrix
- Supports manual dispatch with debugging (includes tmate session on failure)

**`.github/workflows/release-to-galaxy.yml`** - Publishing automation:
- Triggered on git tags
- Publishes role to Ansible Galaxy

**`.github/workflows/gh-pages.yml`** - Documentation:
- Generates HTML from AsciiDoc using asciidoctor-reducer
- Publishes to GitHub Pages

## Documentation Pattern

Generated roles use a dual-format documentation strategy:

- **`README.orig.adoc`**: Source with `include::` directives
- **`README.adoc`**: Flattened version for GitHub (GitHub doesn't support includes)
- **HTML on GitHub Pages**: Properly rendered with includes

**Regenerating README.adoc:**
The `gh-pages.yml` workflow automatically flattens README.orig.adoc using asciidoctor-reducer.

## Development Container

Generated roles include `.devcontainer/devcontainer.json` for VS Code:
- Docker-in-Docker support (for running Molecule)
- Pre-configured extensions (Ansible, Python, Git)
- Python 3.12 environment

To use:
1. Install VS Code + Dev Containers extension
2. Open folder in VS Code
3. Command: "Remote-Containers: Open Folder in Container"

## Key Files to Edit When Modifying Template

**Template Configuration:**
- `cookiecutter.json`: Template variables and prompts
- `hooks/pre_gen_project.py`: Validation logic

**Generated Role Structure:**
- `{{ cookiecutter.project_slug }}/defaults/main.yml`: User-overridable variables
- `{{ cookiecutter.project_slug }}/vars/main.yml`: OS-specific variable mappings
- `{{ cookiecutter.project_slug }}/tasks/main.yml`: Main task execution
- `{{ cookiecutter.project_slug }}/tasks/assert.yml`: Variable validation
- `{{ cookiecutter.project_slug }}/molecule/`: Testing configuration
- `{{ cookiecutter.project_slug }}/.github/workflows/`: CI/CD pipelines

**Template Testing:**
- `.github/workflows/ci.yml`: Tests the template generation itself
- `.github/cookiecutter-example.yml`: Example config for CI

## Pre-commit Hooks

Both template and generated roles use extensive pre-commit automation:

**General:** YAML/JSON/TOML validation, trailing whitespace, detect-secrets
**Python:** pyupgrade, black, flake8, mypy, reorder_python_imports
**Ansible:** yamllint, ansible-lint (generated roles only)
**Formatting:** prettier (Markdown, JSON, YAML)
**Commit Messages:** commitlint (conventional commits)

## Quality Gates

1. **Pre-commit (local/CI)**: Syntax validation, formatting, linting, security scanning
2. **CI Lint Stage**: YAML validation across all files
3. **CI Molecule Stage**: Functional tests across distribution × Ansible version matrix
4. **Tag-based Release**: Automatic Galaxy publishing

## Renovate Integration

Generated roles include `renovate.json5` for automated dependency updates. Users must enable Renovate via GitHub App installation.
