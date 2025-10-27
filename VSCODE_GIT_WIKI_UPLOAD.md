# Upload Wikis to Azure DevOps usando VS Code + Git + SSO

## ✅ Configuración Previa

**Usuario**: fuad.onate@CompanyX.com
**Autenticación**: SSO (Okta)
**Herramienta**: VS Code con Git integrado
**Proyecto**: GIS - SECURITY_ANALYTICS - DW

---

## Paso 1: Configurar Git Credential Manager (Una sola vez)

Git Credential Manager (GCM) maneja la autenticación SSO automáticamente.

### Opción A: Si GCM ya está instalado (viene con Git for Windows)

Verificar instalación:
```bash
git credential-manager version
```

Si está instalado, configurar para Azure DevOps:
```bash
git config --global credential.helper manager
git config --global user.email "fuad.onate@CompanyX.com"
git config --global user.name "Fuad Onate"
```

### Opción B: Si necesitas instalar GCM

Descargar desde: https://github.com/git-ecosystem/git-credential-manager/releases/latest

O instalar via winget:
```powershell
winget install --id Git.Git -e --source winget
```

---

## Paso 2: Abrir Terminal Integrado en VS Code

1. En VS Code, presiona **Ctrl + `** (backtick) para abrir terminal
2. O ve a **Terminal** → **New Terminal**
3. Asegúrate de estar en PowerShell o Git Bash

---

## Paso 3: Navegar al Directorio del Proyecto

```bash
cd "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
```

---

## Paso 4: Clonar el Wiki Repository (Con Autenticación SSO)

```bash
# Clonar el wiki repo
git clone https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki wiki-repo
```

**Lo que pasará**:
1. Git Credential Manager abrirá una ventana del navegador
2. Serás redirigido a Okta para autenticación SSO
3. Inicia sesión con fuad.onate@CompanyX.com
4. Completa MFA si es requerido
5. Autoriza el acceso a Azure DevOps
6. Git guardará las credenciales para futuros usos

**Si aparece error "repository not found"**:
- Significa que la URL del wiki puede ser diferente
- O el wiki aún no existe como repositorio Git

**Alternativa - Crear el Wiki primero desde Azure DevOps**:
1. Ve a: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki
2. Si no existe wiki, haz clic en "Create project wiki"
3. Esto crea el repositorio Git automáticamente
4. Luego intenta clonar nuevamente

---

## Paso 5: Verificar Clonación y Estructura Existente

```bash
# Entrar al wiki-repo
cd wiki-repo

# Ver estructura actual (PowerShell)
Get-ChildItem -Recurse | Select-Object FullName

# O en Git Bash
ls -la
tree -a
```

**⚠️ IMPORTANTE**: Anota qué archivos existen para no sobrescribirlos.

---

## Paso 6: Crear Backup Branch (Seguridad)

```bash
# Ver branch actual
git branch

# Crear backup del estado actual
git checkout -b backup-before-new-wikis-2025-10-24

# Subir backup a Azure DevOps
git push origin backup-before-new-wikis-2025-10-24

# Volver a main
git checkout main
```

Esto te permite revertir si algo sale mal.

---

## Paso 7: Crear Estructura para Nuevas Wikis

```bash
# Crear carpeta para las nuevas wikis
mkdir SECURITY_ANALYTICS-Documentation

# Verificar creación
ls -l SECURITY_ANALYTICS-Documentation
```

---

## Paso 8: Copiar las 6 Wikis al Repositorio

```bash
# Copiar archivos desde directorio padre
Copy-Item "..\WIKI_01_STREAMLIT_APPS.md" -Destination "SECURITY_ANALYTICS-Documentation\01-Streamlit-Applications.md"
Copy-Item "..\WIKI_02_POWER_BI.md" -Destination "SECURITY_ANALYTICS-Documentation\02-Power-BI-Roadmap.md"
Copy-Item "..\WIKI_03_METADATA_EXTRACTION.md" -Destination "SECURITY_ANALYTICS-Documentation\03-Metadata-Extraction.md"
Copy-Item "..\WIKI_04_DATA_GOVERNANCE.md" -Destination "SECURITY_ANALYTICS-Documentation\04-Data-Governance.md"
Copy-Item "..\WIKI_05_DATA_DICTIONARY.md" -Destination "SECURITY_ANALYTICS-Documentation\05-Data-Dictionary.md"
Copy-Item "..\WIKI_06_BEST_PRACTICES.md" -Destination "SECURITY_ANALYTICS-Documentation\06-Best-Practices.md"
```

**O usa VS Code Explorer**:
1. En VS Code, ve al Explorer (Ctrl+Shift+E)
2. Navega a `wiki-repo/SECURITY_ANALYTICS-Documentation/`
3. Arrastra y suelta los 6 archivos WIKI_*.md
4. Renómbralos según el patrón: 01-Streamlit-Applications.md, etc.

---

## Paso 9: Usar Source Control de VS Code

VS Code tiene integración Git visual que es muy útil.

### Abrir Source Control Panel

1. Presiona **Ctrl+Shift+G** o haz clic en el ícono de Git en la barra lateral
2. Verás los cambios pendientes

### Revisar Cambios (CRÍTICO)

En Source Control panel:
- ✅ Deberías ver **6 archivos nuevos** (U = Untracked)
- ❌ NO debes ver archivos modificados (M) que ya existían
- ❌ Si ves archivos existentes modificados, DETENTE e investiga

### Ejemplo de lo que debes ver:
```
Changes (6)
  U SECURITY_ANALYTICS-Documentation/01-Streamlit-Applications.md
  U SECURITY_ANALYTICS-Documentation/02-Power-BI-Roadmap.md
  U SECURITY_ANALYTICS-Documentation/03-Metadata-Extraction.md
  U SECURITY_ANALYTICS-Documentation/04-Data-Governance.md
  U SECURITY_ANALYTICS-Documentation/05-Data-Dictionary.md
  U SECURITY_ANALYTICS-Documentation/06-Best-Practices.md
```

---

## Paso 10: Stage Changes (Agregar a Git)

### Opción A: Usar VS Code Source Control

1. En el panel Source Control, pasa el mouse sobre "Changes"
2. Haz clic en el **+** (plus) al lado de "Changes" para stage todos los archivos
3. O haz clic en **+** al lado de cada archivo individual

### Opción B: Usar Terminal

```bash
# Stage todos los nuevos archivos
git add SECURITY_ANALYTICS-Documentation/

# Verificar qué se va a commit
git status
```

**Salida esperada**:
```
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   SECURITY_ANALYTICS-Documentation/01-Streamlit-Applications.md
        new file:   SECURITY_ANALYTICS-Documentation/02-Power-BI-Roadmap.md
        new file:   SECURITY_ANALYTICS-Documentation/03-Metadata-Extraction.md
        new file:   SECURITY_ANALYTICS-Documentation/04-Data-Governance.md
        new file:   SECURITY_ANALYTICS-Documentation/05-Data-Dictionary.md
        new file:   SECURITY_ANALYTICS-Documentation/06-Best-Practices.md
```

---

## Paso 11: Commit Changes

### Opción A: Usar VS Code Source Control

1. En el panel Source Control, verás un campo de texto arriba que dice "Message"
2. Escribe un mensaje de commit descriptivo:

```
docs: Add comprehensive SECURITY_ANALYTICS Data Warehouse documentation

Add 6 new wiki pages documenting the SECURITY_ANALYTICS Data Warehouse project:

1. Streamlit Applications - Complete catalog of 20 analytics applications
2. Power BI Roadmap - Implementation plan for BI platform (6 months)
3. Metadata Extraction - Automated metadata management system
4. Data Governance - Governance framework and policies
5. Data Dictionary - Complete catalog (20 services, 180 tables, 2,206 columns)
6. Best Practices - Development standards and guidelines

Key Features:
- Complete documentation for 20 integrated security services
- Metadata repository automation (SP_REFRESH_METADATA)
- Daily scheduled metadata refresh
- Comprehensive data governance framework
- SQL and Python development standards

All documentation written in English per project standards.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

3. Presiona **Ctrl+Enter** o haz clic en el checkmark ✓ arriba

### Opción B: Usar Terminal

```bash
git commit -m "docs: Add comprehensive SECURITY_ANALYTICS Data Warehouse documentation

Add 6 new wiki pages documenting the SECURITY_ANALYTICS Data Warehouse project:

1. Streamlit Applications - Complete catalog of 20 analytics applications
2. Power BI Roadmap - Implementation plan for BI platform (6 months)
3. Metadata Extraction - Automated metadata management system
4. Data Governance - Governance framework and policies
5. Data Dictionary - Complete catalog (20 services, 180 tables, 2,206 columns)
6. Best Practices - Development standards and guidelines

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Paso 12: Push a Azure DevOps

### Opción A: Usar VS Code Source Control

1. En el panel Source Control, haz clic en **"..."** (tres puntos) arriba
2. Selecciona **Push** o **Sync Changes**
3. VS Code usará Git Credential Manager para autenticación SSO automáticamente

### Opción B: Usar Terminal

```bash
# Push a Azure DevOps
git push origin main
```

**Lo que pasará**:
- Git Credential Manager usa las credenciales guardadas (SSO)
- Si es la primera vez, abrirá navegador para Okta
- Upload de los 6 archivos a Azure DevOps
- Confirmación del push exitoso

**Salida esperada**:
```
Enumerating objects: 8, done.
Counting objects: 100% (8/8), done.
Delta compression using up to 8 threads
Compressing objects: 100% (6/6), done.
Writing objects: 100% (7/7), 225.00 KiB | 15.00 MiB/s, done.
Total 7 (delta 1), reused 0 (delta 0)
remote: Analyzing objects... (7/7) (100 ms)
remote: Storing packfile... done (50 ms)
To https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki
   abc1234..def5678  main -> main
```

---

## Paso 13: Verificar en Azure DevOps

1. Abre tu navegador
2. Ve a: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/
3. Deberías ver:
   - ✅ Nueva carpeta "SECURITY_ANALYTICS-Documentation"
   - ✅ 6 wikis dentro de la carpeta
   - ✅ Formatting correcto (tablas, código, etc.)
   - ✅ Table of contents funcional
   - ✅ Links internos funcionando

---

## Troubleshooting

### Error: "repository not found"

**Causa**: El wiki no existe como repositorio Git todavía.

**Solución**:
1. Ve a Azure DevOps web interface
2. Navega a Wiki section del proyecto
3. Haz clic en "Create project wiki" si no existe
4. Esto crea el repositorio Git automáticamente
5. Intenta clonar nuevamente

### Error: "Authentication failed"

**Causa**: Credenciales no guardadas o expiradas.

**Solución**:
```bash
# Limpiar credenciales
git credential-manager erase https://dev.azure.com

# Intentar clonar nuevamente (abrirá ventana SSO)
git clone https://dev.azure.com/CompanyX/...
```

### Error: "Permission denied"

**Causa**: Tu cuenta no tiene permisos de Contributor en el wiki.

**Solución**:
- Contactar al Project Administrator
- Solicitar rol "Contributor" para el wiki
- Verificar permisos en Project Settings → Permissions

### VS Code no muestra cambios en Source Control

**Solución**:
```bash
# Refrescar Git status
git status

# Recargar ventana de VS Code
# Ctrl+Shift+P → "Reload Window"
```

### Push falla con "rejected"

**Causa**: El remote tiene cambios que no tienes localmente.

**Solución**:
```bash
# Pull primero
git pull origin main

# Resolver conflictos si los hay
# Luego push
git push origin main
```

---

## Verificación Final

Checklist después del push:

- [ ] Las 6 wikis están visibles en Azure DevOps
- [ ] El formatting se ve correcto (tablas, código, etc.)
- [ ] Los links internos funcionan
- [ ] El Table of Contents funciona
- [ ] No se modificaron wikis existentes
- [ ] Backup branch creado y subido

---

## Comandos Rápidos (Resumen)

Si todo está configurado, estos son los comandos esenciales:

```bash
# 1. Clonar
git clone https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki wiki-repo
cd wiki-repo

# 2. Backup
git checkout -b backup-before-new-wikis-2025-10-24
git push origin backup-before-new-wikis-2025-10-24
git checkout main

# 3. Crear estructura
mkdir SECURITY_ANALYTICS-Documentation

# 4. Copiar archivos (PowerShell)
Copy-Item "..\WIKI_0*.md" -Destination "SECURITY_ANALYTICS-Documentation\"
# (Renombrar según patrón 01-Streamlit-Applications.md)

# 5. Commit y push
git add SECURITY_ANALYTICS-Documentation/
git commit -m "docs: Add comprehensive SECURITY_ANALYTICS Data Warehouse documentation"
git push origin main
```

---

## Próximos Pasos

Después de subir las wikis:

1. **Verificar upload** en Azure DevOps
2. **Actualizar links** en wiki home page (si existe)
3. **Notificar equipo** vía email/Teams
4. **Mejorar ERD** del Data Model wiki (ejecutar GENERATE_ERD_FROM_METADATA.sql)
5. **Programar review** de wikis con stakeholders

---

**Documento Creado**: 2025-10-24
**Usuario**: fuad.onate@CompanyX.com
**Autenticación**: SSO (Okta) via Git Credential Manager
**Herramienta**: VS Code + Git integrado
**Status**: Listo para ejecutar
