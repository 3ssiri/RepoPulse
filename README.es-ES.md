# RepoPulse

[![CI](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml/badge.svg)](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/repopulse-cli.svg)](https://pypi.org/project/repopulse-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

RepoPulse es una CLI en Python que escanea repositorios de GitHub (o una carpeta local) y produce un **informe de salud**: puntuación sobre 100, comprobaciones pass/warn/fail y recomendaciones accionables.

| | Nombre correcto |
|---|---|
| **Instalar desde PyPI** | `repopulse-cli` |
| **Comando CLI** | `repopulse` |
| **Import en Python** | `repopulse` |

> **Importante:** no uses `pip install repopulse` — es **otro** paquete en PyPI. Usa siempre **`repopulse-cli`**.

## Instalación (usuarios)

```bash
pip install repopulse-cli
repopulse --help
```

Actualizar:

```bash
pip install -U repopulse-cli
```

Desde el código fuente (contribuidores):

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e ".[dev]"
```

Guía completa: [INSTALLATION.md](INSTALLATION.md) (en inglés).

## Inicio rápido

```bash
# Carpeta local (sin API de GitHub)
repopulse scan .

# Repositorio público
repopulse scan https://github.com/psf/requests

# Rama o etiqueta sin clonar
repopulse scan https://github.com/owner/repo/tree/main
repopulse scan https://github.com/owner/repo --ref v1.0.0

# Comparar dos refs
repopulse compare \
  https://github.com/owner/repo/tree/main \
  https://github.com/owner/repo/tree/feature/x \
  --fail-on-regression

# Vista previa de issues (seguro)
repopulse create-issues https://github.com/owner/repo --dry-run

# Umbral para CI
repopulse scan . --fail-under 75 --format summary --quiet
```

Todas las opciones: [USAGE.md](USAGE.md).

## Características actuales

- Escaneo remoto (GitHub) y **local offline** (`scan .`)
- Refs remotos: `/tree/<ref>`, `/releases/tag/<tag>`, `--ref`
- `compare` con deltas y `--fail-on-regression`
- `create-issues` con `--dry-run` / `--yes`
- Formatos: `table`, `summary`, `markdown`, `json`, `issues`
- Config `.repopulse.yml` y perfiles: `strict`, `library`, `docs`, `release`
- Detección de nombres de archivos sensibles **sin** imprimir secretos
- Ejemplo de GitHub Actions: [examples/github-action-repopulse.yml](examples/github-action-repopulse.yml)

## Enlaces

- [README en inglés](README.md)
- [README en árabe](README.ar.md)
- [Instalación](INSTALLATION.md)
- [Uso](USAGE.md)
- [Comprobaciones](docs/checks.md)
- [Changelog](CHANGELOG.md)
- [PyPI](https://pypi.org/project/repopulse-cli/)

## Licencia

MIT — ver [LICENSE](LICENSE).
