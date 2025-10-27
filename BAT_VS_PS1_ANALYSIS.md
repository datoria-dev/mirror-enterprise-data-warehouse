# .BAT vs .PS1 for Deployment Scripts - Analysis & Recommendations

**Date**: 2025-10-27
**Project**: SECURITY_ANALYTICS Streamlit Apps Deployment
**Current**: 20 .bat files for various tasks

---

## 🎯 Executive Summary

### Recomendación: **Migrar a PowerShell (.ps1)** pero mantener algunos .bat para compatibilidad

**Razón Principal**: PowerShell ofrece mejor error handling, logging, y mantenibilidad
**Estrategia**: Usar .ps1 para scripts complejos, .bat para launchers simples

---

## 📊 Comparación Detallada: .BAT vs .PS1

### 1. **Sintaxis y Legibilidad**

#### .BAT (Batch Files)
```batch
@echo off
REM This is a comment
set VAR=value
echo %VAR%
if %ERRORLEVEL% NEQ 0 (
    echo Error occurred
    exit /b 1
)
```

**Pros**:
- ✅ Sintaxis simple para tareas básicas
- ✅ Todos conocen los comandos básicos
- ✅ No requiere PowerShell habilitado

**Cons**:
- ❌ Sintaxis arcaica (de DOS, años 80)
- ❌ Difícil de leer scripts complejos
- ❌ Variables con %% confusas
- ❌ Manejo de errores limitado

---

#### .PS1 (PowerShell Scripts)
```powershell
# This is a comment
$var = "value"
Write-Host $var
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error occurred"
    exit 1
}
```

**Pros**:
- ✅ Sintaxis moderna y clara
- ✅ Fácil de leer y mantener
- ✅ Variables con $ claras
- ✅ Error handling robusto

**Cons**:
- ⚠️ Requiere PowerShell (viene con Windows 10+)
- ⚠️ Execution policy puede bloquear scripts
- ⚠️ Curva de aprendizaje inicial

---

### 2. **Error Handling**

#### .BAT
```batch
@echo off
python script.py
if %ERRORLEVEL% NEQ 0 (
    echo Script failed with code %ERRORLEVEL%
    pause
    exit /b 1
)
echo Success!
```

**Limitaciones**:
- ❌ Solo chequea ERRORLEVEL (código de salida)
- ❌ No captura output de error
- ❌ Difícil hacer try-catch
- ❌ No hay stack traces

---

#### .PS1
```powershell
try {
    python script.py
    if ($LASTEXITCODE -ne 0) {
        throw "Script failed with exit code $LASTEXITCODE"
    }
    Write-Host "Success!" -ForegroundColor Green
}
catch {
    Write-Error "Error: $_"
    Write-Error $_.Exception.StackTrace
    Read-Host "Press Enter to exit"
    exit 1
}
```

**Ventajas**:
- ✅ Try-catch-finally completo
- ✅ Captura excepciones detalladas
- ✅ Stack traces disponibles
- ✅ Error logging robusto

---

### 3. **Logging y Output**

#### .BAT
```batch
@echo off
echo Starting deployment... >> deploy.log
python deploy.py >> deploy.log 2>&1
echo Deployment complete >> deploy.log
type deploy.log
```

**Limitaciones**:
- ❌ Logging básico (solo append a archivo)
- ❌ No hay timestamps automáticos
- ❌ Difícil formatear output
- ❌ No hay niveles de log (INFO, WARN, ERROR)

---

#### .PS1
```powershell
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    Add-Content -Path "deploy.log" -Value $logMessage

    switch ($Level) {
        "INFO"  { Write-Host $logMessage -ForegroundColor Cyan }
        "WARN"  { Write-Host $logMessage -ForegroundColor Yellow }
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
    }
}

Write-Log "Starting deployment..." "INFO"
python deploy.py
Write-Log "Deployment complete" "INFO"
```

**Ventajas**:
- ✅ Funciones personalizadas de logging
- ✅ Timestamps automáticos
- ✅ Colores para diferentes niveles
- ✅ Formato consistente
- ✅ Logging a archivo Y consola simultáneamente

---

### 4. **Manejo de Parámetros**

#### .BAT
```batch
@echo off
set APP=%1
set ENV=%2

if "%APP%"=="" (
    echo Usage: deploy.bat [app_name] [environment]
    exit /b 1
)

echo Deploying %APP% to %ENV%
```

**Limitaciones**:
- ❌ Parámetros posicionales solo (%1, %2, etc.)
- ❌ No hay parámetros nombrados
- ❌ Validación manual tediosa
- ❌ No hay valores por defecto fáciles

---

#### .PS1
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$AppName,

    [Parameter(Mandatory=$false)]
    [ValidateSet("DEV", "PROD")]
    [string]$Environment = "DEV",

    [switch]$Force
)

Write-Host "Deploying $AppName to $Environment"
if ($Force) {
    Write-Host "Force mode enabled"
}
```

**Ventajas**:
- ✅ Parámetros nombrados y posicionales
- ✅ Validación automática
- ✅ Valores por defecto
- ✅ Parámetros obligatorios marcados
- ✅ Help automático (-?)
- ✅ Switches (boolean flags)

---

### 5. **Funciones y Reutilización**

#### .BAT
```batch
@echo off
REM No hay funciones reales, solo labels
call :DeployApp "Sophos"
call :DeployApp "Trellix"
goto :eof

:DeployApp
echo Deploying %~1
python deploy.py --app=%~1
goto :eof
```

**Limitaciones**:
- ❌ "Funciones" con CALL/GOTO (arcaico)
- ❌ No hay return values
- ❌ No hay scoping de variables
- ❌ Difícil modularizar

---

#### .PS1
```powershell
function Deploy-StreamlitApp {
    param(
        [string]$AppName,
        [string]$Stage = "STREAMLIT_APPS_STAGE"
    )

    Write-Log "Deploying $AppName..." "INFO"

    $result = python deploy.py --app=$AppName --stage=$Stage

    if ($LASTEXITCODE -eq 0) {
        Write-Log "Successfully deployed $AppName" "INFO"
        return $true
    } else {
        Write-Log "Failed to deploy $AppName" "ERROR"
        return $false
    }
}

# Usar función
$success = Deploy-StreamlitApp -AppName "Sophos"
if ($success) {
    Deploy-StreamlitApp -AppName "Trellix"
}
```

**Ventajas**:
- ✅ Funciones reales con parámetros
- ✅ Return values
- ✅ Variable scoping correcto
- ✅ Fácil modularizar y reutilizar
- ✅ Puede importar módulos (.psm1)

---

### 6. **Progreso y UI**

#### .BAT
```batch
@echo off
echo [1/5] Starting...
timeout /t 2 /nobreak >nul
echo [2/5] Uploading...
timeout /t 2 /nobreak >nul
echo [3/5] Creating app...
```

**Limitaciones**:
- ❌ Solo texto plano
- ❌ No hay progress bars
- ❌ Difícil mostrar estado visual

---

#### .PS1
```powershell
$apps = @("Sophos", "Trellix", "Zerofox")
$i = 0

foreach ($app in $apps) {
    $i++
    $percent = ($i / $apps.Count) * 100

    Write-Progress -Activity "Deploying Apps" `
                   -Status "Deploying $app" `
                   -PercentComplete $percent

    Deploy-StreamlitApp -AppName $app
    Start-Sleep -Seconds 2
}

Write-Progress -Activity "Deploying Apps" -Completed
```

**Ventajas**:
- ✅ Progress bars nativos
- ✅ Porcentajes de completado
- ✅ Estado visual claro
- ✅ UI más profesional

---

## 📋 Análisis de Tus Scripts Actuales

### Scripts .BAT Actuales (20 archivos)

**Deployment Scripts**:
1. `deploy_apps.bat` - Deployment general
2. `deploy_all_apps_fixed.bat` - Deploy 18 apps con fixes
3. `deploy_sophos_only.bat` - Deploy solo Sophos
4. `deploy_sophos_fixed.bat` - Deploy Sophos con fixes
5. `redeploy_sophos_all_fixes.bat` - Redeploy Sophos
6. `deploy_symantec.bat` - Deploy Symantec

**Utility Scripts**:
7. `verify_apps.bat` - Verificar apps
8. `check_stage.bat` - Chequear stage
9. `analyze_logs.bat` - Analizar logs
10. `fix_apps.bat` - Aplicar fixes

**Infrastructure**:
11. `connect_snowsql_sso.bat` - Conectar SnowSQL
12. `test_snowsql_connection.bat` - Test conexión
13. `install_snowsql.bat` - Instalar SnowSQL
14. `reinstall_snowsql.bat` - Reinstalar

**Git/Azure**:
15. `push_to_azure.bat` - Push a Azure DevOps

**OneDrive Management** (parece legacy):
16-20. Scripts de OneDrive (probablemente obsoletos)

---

## 🎯 Recomendación: Estrategia Híbrida

### Enfoque Recomendado

**Usar .PS1 para**:
- ✅ Scripts complejos de deployment
- ✅ Scripts con error handling avanzado
- ✅ Scripts con logging detallado
- ✅ Scripts que procesan múltiples apps
- ✅ Scripts para documentación

**Usar .BAT para**:
- ✅ Launchers simples (llaman a .ps1)
- ✅ Compatibilidad con sistemas antiguos
- ✅ Scripts muy simples (1-5 líneas)
- ✅ Quick access desde Explorer (doble click)

---

## 📝 Estructura Propuesta

### Para cada tarea principal, tener:

```
deployment/
├── Deploy-StreamlitApps.ps1          # Script principal PowerShell
├── deploy.bat                         # Launcher simple
└── README.md                          # Documentación

Deploy-StreamlitApps.ps1 (completo, bien documentado)
deploy.bat (simple launcher)
```

**Ejemplo deploy.bat (launcher)**:
```batch
@echo off
powershell -ExecutionPolicy Bypass -File "deployment\Deploy-StreamlitApps.ps1" %*
```

**Beneficios**:
- ✅ Doble click en .bat funciona
- ✅ Lógica compleja en .ps1 (mantenible)
- ✅ Compatibilidad máxima

---

## 📄 Ejemplo Completo: Deployment Script

### Versión .BAT Actual
```batch
@echo off
echo Deploying all fixed apps...
python "02_PYTHON_SCRIPTS\deploy_all_apps_fixed.py"
if %ERRORLEVEL% NEQ 0 (
    echo Deployment failed
    pause
    exit /b 1
)
echo Deployment complete
pause
```

**Problemas**:
- ❌ No logging
- ❌ No progress indicator
- ❌ Error handling básico
- ❌ No validación de pre-requisitos

---

### Versión .PS1 Propuesta
```powershell
<#
.SYNOPSIS
    Deploy all fixed Streamlit apps to Snowflake

.DESCRIPTION
    This script deploys all 18 SECURITY_ANALYTICS Streamlit apps with:
    - Fixed syntax errors (Trellix, Crowdstrike)
    - CPR - prefix in titles
    - Updated dummy classes

.PARAMETER Environment
    Target environment (DEV or PROD). Default: DEV

.PARAMETER AppsToDepl oy
    Specific apps to deploy. If not specified, deploys all 18.

.PARAMETER SkipValidation
    Skip pre-deployment validation checks

.EXAMPLE
    .\Deploy-StreamlitApps.ps1
    Deploy all apps to DEV

.EXAMPLE
    .\Deploy-StreamlitApps.ps1 -AppsTo Deploy @("Sophos", "Trellix")
    Deploy only Sophos and Trellix

.NOTES
    Author: SECURITY_ANALYTICS Team
    Date: 2025-10-27
    Version: 1.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("DEV", "PROD")]
    [string]$Environment = "DEV",

    [Parameter(Mandatory=$false)]
    [string[]]$AppsToDeploy = @(),

    [switch]$SkipValidation
)

# =============================================================================
# Configuration
# =============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $ScriptDir "deployment_logs\deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

$AllApps = @(
    "Ancon", "BitSight", "Cisco_AMP", "Crowdstrike", "CybelAngel",
    "Intel_Threats", "Leviat", "Proofpoint", "Qualys", "SentinelOne",
    "ServiceNow", "Sophos", "Splunk", "Symantec", "Tenable",
    "Trellix", "Zerofox", "Zscaler"
)

# =============================================================================
# Functions
# =============================================================================

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    # Write to file
    Add-Content -Path $LogFile -Value $logMessage

    # Write to console with color
    switch ($Level) {
        "INFO"    { Write-Host $logMessage -ForegroundColor Cyan }
        "WARN"    { Write-Host $logMessage -ForegroundColor Yellow }
        "ERROR"   { Write-Host $logMessage -ForegroundColor Red }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
    }
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..." "INFO"

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python found: $pythonVersion" "SUCCESS"
    }
    catch {
        Write-Log "Python not found. Please install Python." "ERROR"
        return $false
    }

    # Check SnowSQL
    $snowsqlPath = "C:\Program Files\Snowflake SnowSQL\snowsql.exe"
    if (Test-Path $snowsqlPath) {
        Write-Log "SnowSQL found at $snowsqlPath" "SUCCESS"
    }
    else {
        Write-Log "SnowSQL not found at $snowsqlPath" "ERROR"
        return $false
    }

    # Check script directory
    $scriptPath = Join-Path $ScriptDir "02_PYTHON_SCRIPTS\deploy_all_apps_fixed.py"
    if (Test-Path $scriptPath) {
        Write-Log "Deployment script found" "SUCCESS"
    }
    else {
        Write-Log "Deployment script not found at $scriptPath" "ERROR"
        return $false
    }

    return $true
}

function Deploy-App {
    param([string]$AppName)

    Write-Log "Deploying $AppName..." "INFO"

    try {
        $appPath = Join-Path $ScriptDir "13_STREAMLIT_COMPLETE\$AppName"

        if (-not (Test-Path $appPath)) {
            Write-Log "App directory not found: $appPath" "ERROR"
            return $false
        }

        # Upload to stage (placeholder - actual implementation)
        Write-Log "Uploading $AppName files to stage..." "INFO"

        # Create/Replace Streamlit (placeholder)
        Write-Log "Creating/Replacing STREAMLIT_$($AppName.ToUpper())..." "INFO"

        Write-Log "Successfully deployed $AppName" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Failed to deploy $AppName: $_" "ERROR"
        return $false
    }
}

# =============================================================================
# Main Script
# =============================================================================

try {
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "DEPLOYING STREAMLIT APPS TO SNOWFLAKE" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host ""

    Write-Log "Starting deployment to $Environment environment" "INFO"
    Write-Log "Log file: $LogFile" "INFO"
    Write-Host ""

    # Validate prerequisites
    if (-not $SkipValidation) {
        if (-not (Test-Prerequisites)) {
            throw "Prerequisites check failed"
        }
        Write-Host ""
    }

    # Determine apps to deploy
    if ($AppsToDeploy.Count -eq 0) {
        $AppsToDeploy = $AllApps
        Write-Log "Deploying all $($AllApps.Count) apps" "INFO"
    }
    else {
        Write-Log "Deploying $($AppsToDeploy.Count) specific apps" "INFO"
    }
    Write-Host ""

    # Deploy apps with progress
    $successCount = 0
    $failCount = 0
    $i = 0

    foreach ($app in $AppsToDeploy) {
        $i++
        $percent = ($i / $AppsToDeploy.Count) * 100

        Write-Progress -Activity "Deploying Streamlit Apps" `
                       -Status "[$i/$($AppsToDeploy.Count)] Deploying $app" `
                       -PercentComplete $percent

        if (Deploy-App -AppName $app) {
            $successCount++
        }
        else {
            $failCount++
        }

        Write-Host ""
    }

    Write-Progress -Activity "Deploying Streamlit Apps" -Completed

    # Summary
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Log "Successful: $successCount" "SUCCESS"
    Write-Log "Failed: $failCount" $(if ($failCount -eq 0) { "SUCCESS" } else { "ERROR" })
    Write-Log "Total: $($AppsToDeploy.Count)" "INFO"
    Write-Host ""
    Write-Log "Log file: $LogFile" "INFO"
    Write-Host "=" * 80 -ForegroundColor Cyan

    if ($failCount -gt 0) {
        exit 1
    }
}
catch {
    Write-Log "Deployment failed: $_" "ERROR"
    Write-Log $_.Exception.StackTrace "ERROR"
    Read-Host "Press Enter to exit"
    exit 1
}
```

---

## 🚀 Recomendaciones Específicas para Tu Proyecto

### 1. **Scripts Prioritarios para Migrar a .PS1**

#### Alta Prioridad (hacer ahora):
1. **Deploy-StreamlitApps.ps1** - Deployment principal con todas las apps
2. **Test-SnowflakeConnection.ps1** - Verificar conexión y permisos
3. **Verify-Apps.ps1** - Verificar estado de apps desplegadas

#### Media Prioridad:
4. **Update-SingleApp.ps1** - Actualizar una app específica
5. **Get-DeploymentStatus.ps1** - Chequear estado del deployment

### 2. **Scripts que Pueden Quedar como .BAT**

- `deploy.bat` - Simple launcher para Deploy-StreamlitApps.ps1
- `connect.bat` - Quick launcher para abrir SnowSQL
- `push.bat` - Simple git push a Azure

### 3. **Organización Propuesta**

```
project/
├── deployment/
│   ├── Deploy-StreamlitApps.ps1     # Main deployment
│   ├── Update-SingleApp.ps1          # Single app update
│   ├── Test-Prerequisites.ps1        # Check environment
│   └── README.md                     # Documentation
│
├── scripts/                           # Utility scripts
│   ├── Test-SnowflakeConnection.ps1
│   ├── Verify-Apps.ps1
│   └── Get-DeploymentLogs.ps1
│
├── launchers/                         # Simple .bat launchers
│   ├── deploy.bat                    # Calls Deploy-StreamlitApps.ps1
│   ├── test-connection.bat
│   └── verify.bat
│
└── 02_PYTHON_SCRIPTS/                # Python scripts (keep as is)
    └── deploy_all_apps_fixed.py
```

---

## 📚 Documentación: .BAT vs .PS1

### Para Documentación Oficial

**Recomendación**: **Usar .PS1 con comentarios detallados**

**Razones**:
1. ✅ **Get-Help integrado**: PowerShell tiene sistema de help nativo
2. ✅ **IntelliSense**: Mejor soporte en VSCode y otros editores
3. ✅ **Ejemplos en código**: Puedes incluir .EXAMPLE en comentarios
4. ✅ **Mantenibilidad**: Más fácil actualizar y documentar
5. ✅ **Profesional**: Scripts .ps1 son el estándar moderno

**Formato de Documentación PowerShell**:
```powershell
<#
.SYNOPSIS
    Brief description

.DESCRIPTION
    Detailed description

.PARAMETER ParameterName
    Parameter description

.EXAMPLE
    Example usage

.NOTES
    Additional notes
#>
```

Este formato genera help automático:
```powershell
Get-Help .\Deploy-StreamlitApps.ps1 -Full
```

---

## ✅ Recomendación Final

### Para Tu Proyecto SECURITY_ANALYTICS:

1. **MIGRAR a PowerShell (.ps1)** los scripts de deployment principales
   - Deploy-StreamlitApps.ps1 (reemplaza deploy_all_apps_fixed.bat)
   - Test-SnowflakeConnection.ps1
   - Verify-Apps.ps1

2. **MANTENER .BAT** como launchers simples
   - deploy.bat → llama Deploy-StreamlitApps.ps1
   - Fácil acceso con doble click

3. **DOCUMENTAR** usando comentarios .ps1
   - Get-Help integrado
   - Ejemplos en el código
   - Más profesional y mantenible

### Próximos Pasos:

1. ⭐ Crear Deploy-StreamlitApps.ps1 (el script principal)
2. ⭐ Crear deploy.bat (launcher simple)
3. Probar deployment con nuevo script
4. Migrar otros scripts gradualmente

**¿Quieres que cree el Deploy-StreamlitApps.ps1 completo ahora?** 😊
