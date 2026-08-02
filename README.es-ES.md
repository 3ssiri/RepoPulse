# RepoPulse

[![CI](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml/badge.svg)](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml)
[![CodeQL](https://github.com/3ssiri/RepoPulse/actions/workflows/codeql.yml/badge.svg)](https://github.com/3ssiri/RepoPulse/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

RepoPulse es una herramienta de CLI en Python que escanea repositorios de GitHub y produce un informe de salud práctico con una puntuación sobre 100, advertencias claras y recomendaciones accionables.

Está diseñada para desarrolladores que desean una revisión rápida de la calidad del repositorio desde la terminal, y para mantenedores que buscan una herramienta ligera que puedan ejecutar posteriormente en su CI.

## Enlaces Rápidos

- [README en Árabe](README.ar.md)
- [Guía de Instalación](INSTALLATION.md)
- [Guía de Uso](USAGE.md)
- [Requisitos](REQUIREMENTS.md)
- [Verificaciones Soportadas](docs/checks.md)
- [Arquitectura](ARCHITECTURE.md)
- [Contribución](CONTRIBUTING.md)
- [Política de Seguridad](SECURITY.md)
- [Hoja de Ruta](docs/roadmap.md)
- [Licencia](LICENSE)
- [Registro de Cambios](CHANGELOG.md)

## Por qué RepoPulse es Importante

Los mantenedores de código abierto repiten las mismas verificaciones de higiene del repositorio en múltiples proyectos: calidad del README, licencias, CI, pruebas, actividad obsoleta, nombres de archivos sensibles y postura básica de seguridad. RepoPulse convierte esas verificaciones en un informe rápido y repetible que puede ejecutarse localmente o mediante automatización.

El proyecto se encuentra en una etapa temprana, pero está diseñado en torno a flujos de trabajo prácticos para mantenedores: triaje rápido, recomendaciones claras, umbrales de CI y salida legible por máquina para futuras automatizaciones.

## Características

- Escaneo de repositorios públicos de GitHub mediante URL.
- Escaneo de repositorios privados con `--token` o `GITHUB_TOKEN`.
- Obtención de metadatos del repositorio y árbol de archivos recursivo a través de la API de GitHub.
- Calificación de la salud del repositorio sobre 100.
- Renderizado de un informe de terminal enriquecido con Rich.
- Exportación de informes en Markdown.
- Impresión o escritura de informes en JSON.
- Generación de resúmenes compactos para automatización.
- Fallo de trabajos de CI con `--fail-under`.
- Personalización de pesos de verificación y umbrales predeterminados mediante `.repopulse.yml`.
- Detección de nombres de archivos sensibles comunes sin imprimir el contenido de los secretos.
- Recomendaciones asesoras sobre dependencias y línea base de seguridad.

## Stack Tecnológico

RepoPulse está construido con:

| Tecnología | Propósito |
|---|---|
| Python 3.11+ | Runtime principal. |
| Typer | Comandos y opciones de CLI. |
| Requests | Llamadas a la API de GitHub. |
| Rich | Tablas de terminal y salida formateada. |
| Pydantic | Modelos de informe y verificación tipados. |
| python-dotenv | Carga opcional de `GITHUB_TOKEN`. |
| Pytest | Suite de pruebas. |
| Ruff | Linting en CI. |

## Instalación

Clona el repositorio e instálalo en modo editable:

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e .
```

Para desarrollo:

```bash
pip install -e ".[dev]"
```

Consulta [INSTALLATION.md](INSTALLATION.md) para notas completas de configuración.

## Uso Básico

```bash
repopulse scan https://github.com/username/repository
repopulse scan https://github.com/username/repository --export report.md
repopulse scan https://github.com/username/repository --format json --output report.json
repopulse scan https://github.com/username/repository --fail-under 75
repopulse scan https://github.com/username/repository --config .repopulse.yml
repopulse scan https://github.com/username/private-repo --token YOUR_GITHUB_TOKEN
```

También puedes configurar un token en el entorno:

```bash
GITHUB_TOKEN=YOUR_GITHUB_TOKEN repopulse scan https://github.com/username/private-repo
```

Consulta [USAGE.md](USAGE.md) para todas las opciones y ejemplos.

## Casos de Uso para Mantenedores de OSS

- Ejecutar verificaciones de salud del repositorio antes de los lanzamientos.
- Añadir un umbral `--fail-under` al CI para establecer puertas de calidad del proyecto.
- Exportar informes en Markdown para el triaje de incidencias o entrega de mantenimiento.
- Exportar JSON para dashboards, bots o futuros flujos de revisión asistidos por IA.
- Auditar repositorios públicos o privados sin imprimir el contenido de los secretos.

## Ejemplo de Salida

```text
RepoPulse Health Report for psf/requests
Score: 91 / 100 - Excellent

Checks
README Quality      PASS   16/20
License             PASS   10/10
.gitignore          PASS   10/10
Tests               WARN   12/15
GitHub Actions      PASS   15/15
```

## Sistema de Puntuación

| Verificación | Puntos |
|---|---:|
| Calidad del README | 20 |
| Licencia | 10 |
| .gitignore | 10 |
| Pruebas | 15 |
| GitHub Actions | 15 |
| Actividad Reciente | 10 |
| Archivos Sensibles | 10 |
| Estructura del Proyecto | 5 |
| Scripts del Paquete | 5 |

Calificaciones:

| Puntuación | Calificación |
|---|---|
| 90-100 | Excelente |
| 75-89 | Bueno |
| 60-74 | Regular |
| 40-59 | Débil |
| 0-39 | Crítico |

Las verificaciones de dependencias y línea base de seguridad son asesoras en la `v0.1.0`; añaden recomendaciones sin cambiar la puntuación de 100 puntos.

## Configuración

RepoPulse lee automáticamente el archivo `.repopulse.yml` del directorio actual si está presente. También puedes pasar un archivo explícitamente:

```bash
repopulse scan https://github.com/username/repository --config examples/repopulse.yml
```

La configuración admite umbrales de CI predeterminados, verificaciones desactivadas y pesos personalizados:

```yaml
fail_under: 85
disabled_checks:
  - activity
weights:
  readme: 25
  tests: 20
  github_actions: 20
```

Consulta [examples/repopulse.yml](examples/repopulse.yml) para un ejemplo completo.

## Verificaciones Soportadas

- Completitud del README.
- Presencia de licencia.
- Presencia de `.gitignore` y patrones comunes.
- Carpetas de pruebas, archivos de prueba y comandos de prueba del paquete.
- Flujos de trabajo de GitHub Actions para CI, pruebas, linting y builds.
- Actividad reciente basada en `pushed_at`.
- Nombres de archivos sensibles como `.env`, `credentials.json` y claves privadas.
- Estructura del proyecto y desorden en la raíz.
- Scripts del paquete o configuración de proyecto Python.
- Higiene de dependencias a través de lockfiles y Dependabot.
- Línea base de seguridad a través de `SECURITY.md`, Dependabot y CodeQL.

Los detalles completos están en [docs/checks.md](docs/checks.md).

## Requisitos

- Python 3.11 o superior.
- Acceso de red a `api.github.com`.
- Token de GitHub para repositorios privados o límites de tasa de API más altos.

Consulta [REQUIREMENTS.md](REQUIREMENTS.md) para los requisitos de ejecución y desarrollo.

## Contribución

Las contribuciones son bienvenidas. Mantén las verificaciones independientes, devuelve un `CheckResult` y añade pruebas enfocadas para nuevos comportamientos.

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para la configuración, pruebas y flujo de trabajo de contribución.

## Licencia

RepoPulse se publica bajo la Licencia MIT. Consulta [LICENSE](LICENSE).
