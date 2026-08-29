---
inclusion: always
---

# Versionado automático al subir cambios

Cada vez que el usuario pida **subir cambios** al repositorio (cualquier
`git commit` y/o `git push`, o frases como "sube los cambios", "haz push",
"sube a main", "deploy"), DEBES actualizar la versión del build **antes** de
crear el commit.

## Regla

1. Genera la marca de versión con la fecha y hora **local actual** en formato:

   ```
   yyyymmdd_hhmm
   ```

   Ejemplo: `20260829_1057` (2026-08-29, 10:57).

2. Escribe/actualiza esa marca en la variable de entorno **`APP_VERSION`**
   dentro del archivo `.env` en la raíz del proyecto:

   ```
   APP_VERSION=yyyymmdd_hhmm
   ```

   - Si el archivo o la variable no existen, créalos.
   - Si `APP_VERSION` ya existe, reemplaza únicamente su valor conservando el
     resto del archivo.

3. Incluye el `.env` en el mismo commit que sube los cambios, de modo que la
   versión quede registrada junto al código.

## La versión debe ser visible para el usuario

La app expone la versión en la UI mediante `get_app_version()` en `app.py`, que
lee `APP_VERSION` (variable de entorno o `.env`) y la muestra en el encabezado.
Al actualizar la marca, esa versión será la que vea el usuario. No elimines ni
ocultes esa visualización.

## Cómo generar la marca (PowerShell / Windows)

Usa la hora local del sistema, no UTC:

```powershell
$version = Get-Date -Format "yyyyMMdd_HHmm"
```

Snippet para actualizar solo `APP_VERSION` sin tocar el resto de `.env`:

```powershell
$version = Get-Date -Format "yyyyMMdd_HHmm"
$envPath = ".env"
if (Test-Path $envPath) {
    $content = Get-Content $envPath
    if ($content -match '^APP_VERSION=') {
        $content = $content -replace '^APP_VERSION=.*', "APP_VERSION=$version"
    } else {
        $content += "APP_VERSION=$version"
    }
    Set-Content -Path $envPath -Value $content
} else {
    Set-Content -Path $envPath -Value "APP_VERSION=$version"
}
```

> La marca SIEMPRE se calcula con la fecha/hora real del momento del push. No la
> inventes ni reutilices una anterior.

## Orden de operaciones al subir

1. Calcular `yyyymmdd_hhmm` con la hora local.
2. Actualizar `APP_VERSION` en `.env`.
3. `git add` de los archivos del cambio **incluyendo** `.env`.
4. `git commit` (menciona la versión en el mensaje, p. ej.
   `chore: release 20260829_1057` o inclúyela en el cuerpo).
5. `git push`.

## Notas

- En este proyecto `.env` solo guarda `APP_VERSION` y valores no sensibles. Si
  en el futuro se añaden secretos, muévelos fuera del control de versiones y
  ajusta `.gitignore`.
- No confundir `APP_VERSION` (identifica el build) con `runtime.txt` (fija la
  versión de Python para el despliegue).
