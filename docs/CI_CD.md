# Guía de Integración Continua (CI/CD) para el Backend

## ¿Qué es la Integración Continua (CI)?

La Integración Continua (CI) es una práctica de desarrollo de software donde los desarrolladores integran su código en un repositorio compartido con frecuencia, idealmente varias veces al día. Cada integración puede entonces ser verificada por una compilación automática y pruebas automatizadas para detectar errores rápidamente.

## ¿Por qué usar CI/CD?

1. **Detección temprana de errores**: Los problemas se detectan y solucionan más rápido.
2. **Calidad del código**: Las pruebas automatizadas aseguran que el código cumpla con los estándares.
3. **Despliegue confiable**: Los despliegues son más seguros y predecibles.
4. **Retroalimentación rápida**: Los desarrolladores reciben retroalimentación inmediata sobre sus cambios.

## Configuración de GitHub Actions para el Backend

Hemos configurado GitHub Actions para ejecutar automáticamente las pruebas del backend en cada push o pull request. Aquí está cómo funciona:

### Archivo de configuración: `.github/workflows/backend-ci.yml`

```yaml
name: Backend CI

on:
  push:
    paths:
      - 'app/**'
      - 'tests/**'
      - 'poetry.lock'
      - 'pyproject.toml'
  pull_request:
    paths:
      - 'app/**'
      - 'tests/**'
      - 'poetry.lock'
      - 'pyproject.toml'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:6
        ports:
          - 6379:6379
        options: --entrypoint redis-server

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y libpq-dev
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: 1.4.0
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: Set up environment variables
      run: |
        echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db" >> $GITHUB_ENV
        echo "TESTING=true" >> $GITHUB_ENV
        echo "DISABLE_RATE_LIMITING=true" >> $GITHUB_ENV
    
    - name: Install dependencies
      run: |
        poetry install --no-interaction --no-ansi
    
    - name: Run tests
      run: |
        poetry run pytest -v --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        fail_ci_if_error: false
```

## Explicación del flujo de trabajo

1. **Disparadores**: El flujo se activa cuando hay cambios en:
   - Cualquier archivo en `app/`
   - Cualquier archivo en `tests/`
   - Archivos de dependencias (`poetry.lock`, `pyproject.toml`)

2. **Servicios**: Se inician dos servicios en contenedores:
   - **PostgreSQL**: Base de datos para las pruebas
   - **Redis**: Para el caché y limitación de velocidad

3. **Configuración del entorno**:
   - Se configura Python 3.9
   - Se instalan dependencias del sistema
   - Se instala Poetry para la gestión de dependencias
   - Se configuran variables de entorno para pruebas

4. **Ejecución de pruebas**:
   - Se instalan las dependencias del proyecto
   - Se ejecutan las pruebas con cobertura
   - Se sube el informe de cobertura a Codecov

## Cómo funciona en la práctica

1. **Push a una rama**:
   - Se ejecutan automáticamente las pruebas
   - Si fallan, recibirás una notificación
   - Si pasan, el código puede ser fusionado con seguridad

2. **Pull Request**:
   - Las pruebas se ejecutan para la rama de características
   - El PR no puede fusionarse si las pruebas fallan
   - La cobertura de código se muestra en el PR

## Configuración recomendada para desarrolladores

Para ejecutar pruebas localmente de manera similar al entorno de CI:

```bash
# Instalar dependencias
poetry install

# Configurar variables de entorno
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db
export TESTING=true
export DISABLE_RATE_LIMITING=true

# Ejecutar pruebas
poetry run pytest -v --cov=app --cov-report=term-missing
```

## Monitoreo de calidad de código

Además de las pruebas, recomendamos configurar:

1. **Codecov**: Para seguimiento de cobertura de código
2. **SonarCloud**: Para análisis estático de código
3. **Dependabot**: Para actualizaciones de seguridad de dependencias

## Próximos pasos

1. Configurar despliegue continuo (CD) para entornos de desarrollo, staging y producción
2. Agregar más pruebas de integración y de extremo a extremo
3. Implementar análisis de seguridad estática
4. Configurar notificaciones en canales de equipo (Slack, MS Teams, etc.)

## Recursos adicionales

- [Documentación de GitHub Actions](https://docs.github.com/es/actions)
- [Guía de Poetry](https://python-poetry.org/docs/)
- [Pruebas en Python](https://docs.python.org/3/library/unittest.html)
- [Pytest](https://docs.pytest.org/)

---

Este documento es un punto de partida. A medida que el proyecto crezca, deberá actualizarse para reflejar los cambios en la infraestructura y los flujos de trabajo.
