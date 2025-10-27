# 🗑️ Guía para Remover OneDrive de tu Computadora

## ⚠️ IMPORTANTE: Lee Todo Antes de Proceder

OneDrive está causando problemas con tus repositorios git. Es una buena idea removerlo.

---

## ✅ Pre-requisitos (COMPLETAR PRIMERO)

### **1. Backup de Archivos Importantes** ⭐⭐⭐
```
Revisa: C:\Users\fonat\OneDrive\
```

**Archivos que DEBES mover a MYORG_LOCAL**:
- Documentos importantes
- Código fuente
- Configuraciones
- Cualquier cosa que no esté en git

**Ya migramos**:
- ✅ Snowflake_ITSECKPI_Project_DEV → MYORG_LOCAL

### **2. Marcar Repo de OneDrive como Legacy** ⭐⭐
```powershell
cd "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
.\mark_onedrive_as_legacy.bat
```

### **3. Verificar MYORG_LOCAL Tiene Todo** ⭐⭐⭐
```powershell
# Verificar que MYORG_LOCAL tiene todos los archivos
ls "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
```

---

## 🎯 Razones para Remover OneDrive

### **Problemas con Repositorios Git**:
- ❌ Sync conflicts frecuentes
- ❌ File locking durante git operations
- ❌ Corrupted files por sync incompleto
- ❌ Performance lento
- ❌ .git folder puede corromperse

### **Mejores Prácticas**:
- ✅ Git repos deben estar en local folders (NO cloud sync)
- ✅ Use git para version control (no OneDrive)
- ✅ Backup con git remote repos (GitHub, Azure DevOps)

---

## 📋 Pasos para Remover OneDrive

### **Método 1: Script Automático** (Recomendado)

He creado un script que hace todo por ti:

```powershell
# 1. Ejecuta el script de análisis
cd "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
.\find_snowsql_and_remove_onedrive.bat

# 2. El script creará: remove_onedrive.bat

# 3. Ejecuta como Administrador
# Right-click remove_onedrive.bat → Run as Administrator
```

---

### **Método 2: Manual** (Paso a Paso)

#### **Paso 1: Cerrar OneDrive**
```powershell
# Ver si OneDrive está corriendo
tasklist | findstr OneDrive

# Cerrar OneDrive
taskkill /f /im OneDrive.exe
```

#### **Paso 2: Desinstalar OneDrive Personal**
```powershell
# Ejecutar el uninstaller
%LOCALAPPDATA%\Microsoft\OneDrive\OneDriveSetup.exe /uninstall
```

**Si no funciona**, intenta:
```powershell
C:\Users\fonat\AppData\Local\Microsoft\OneDrive\OneDriveSetup.exe /uninstall
```

#### **Paso 3: Desinstalar OneDrive Business** (Si aplica)
```powershell
# 64-bit
"%PROGRAMFILES%\Microsoft OneDrive\OneDriveSetup.exe" /uninstall

# 32-bit (si el anterior no funciona)
"%PROGRAMFILES(X86)%\Microsoft OneDrive\OneDriveSetup.exe" /uninstall
```

#### **Paso 4: Esperar Desinstalación**
- Espera 1-2 minutos
- Verifica que OneDrive ya no aparece en procesos: `tasklist | findstr OneDrive`

#### **Paso 5: Remover Folder de OneDrive**
```powershell
# ⚠️ ASEGÚRATE DE HABER HECHO BACKUP PRIMERO!

# Remover folder completo
rd "C:\Users\fonat\OneDrive" /s /q
```

#### **Paso 6: Limpiar Registry** (Opcional)
```powershell
# Remover keys de OneDrive
reg delete "HKCU\Software\Microsoft\OneDrive" /f

# Remover del explorer namespace
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" /f
```

#### **Paso 7: Prevenir Auto-Start** (Opcional)
```powershell
# Deshabilitar OneDrive permanentemente
reg add "HKLM\Software\Policies\Microsoft\Windows\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1 /f
```

---

## 🧪 Verificación Post-Remoción

### **Check 1: OneDrive Process**
```powershell
tasklist | findstr OneDrive
# Resultado esperado: No debería aparecer nada
```

### **Check 2: OneDrive Folder**
```powershell
Test-Path "C:\Users\fonat\OneDrive"
# Resultado esperado: False
```

### **Check 3: File Explorer**
- Abre File Explorer
- En el panel izquierdo, NO debería aparecer "OneDrive"

### **Check 4: System Tray**
- Revisa la bandeja del sistema (abajo a la derecha)
- NO debería aparecer el ícono de OneDrive (nube)

---

## 🔄 Alternativas a OneDrive

### **Para Backup de Archivos**:
1. **External Hard Drive** - Backup local
2. **Google Drive** - Solo para archivos NO-GIT
3. **Dropbox** - Solo para archivos NO-GIT
4. **Azure Backup** - Enterprise solution

### **Para Repositorios Git**:
1. **GitHub** - Repositorios públicos/privados
2. **Azure DevOps** - Enterprise git hosting
3. **GitLab** - Alternative to GitHub
4. **Bitbucket** - Atlassian solution

### **Mejor Práctica**:
```
📁 C:\Users\fonat\Documents\
  ├── MYORG_LOCAL\              ← Git repos (NO cloud sync)
  │   └── Projects\
  │       ├── .git\
  │       └── code\
  │
  └── CloudSync\              ← Cloud-synced files (NO git)
      └── Documents\
          └── non-code files
```

**Regla Simple**:
- ✅ Git repos → Local folders (C:\Users\fonat\Documents\)
- ✅ Non-git files → Cloud sync OK

---

## 📝 Checklist Pre-Remoción

Antes de remover OneDrive, verifica:

- [ ] **Backup completo** de archivos importantes en OneDrive
- [ ] **MYORG_LOCAL tiene** todos los proyectos de código
- [ ] **OneDrive repo marcado** como LEGACY
- [ ] **No hay archivos abiertos** desde OneDrive
- [ ] **VSCode/editors cerrados** (no tienen archivos de OneDrive abiertos)
- [ ] **Git commits están pusheados** a remote repos

---

## 🐛 Troubleshooting

### **Problema: "File is being used by another process"**

**Solución**:
1. Cierra todos los programas
2. Abre Task Manager (Ctrl+Shift+Esc)
3. Busca "OneDrive" en Processes
4. End task para todos los procesos de OneDrive
5. Intenta de nuevo

### **Problema: "Access Denied"**

**Solución**:
- Ejecuta PowerShell como Administrador
- Right-click PowerShell → Run as Administrator

### **Problema: OneDrive se reinstala solo**

**Causa**: Windows Update puede reinstalar OneDrive

**Solución**:
```powershell
# Deshabilitar permanentemente
reg add "HKLM\Software\Policies\Microsoft\Windows\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1 /f
```

### **Problema: Folder de OneDrive no se borra**

**Solución**:
1. Reinicia la computadora
2. Intenta borrar de nuevo
3. Si persiste, usa: `rd /s /q "C:\Users\fonat\OneDrive"`

---

## 🎯 Después de Remover OneDrive

### **Paso 1: Verificar Git Repos**
```powershell
cd "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
git status
```

### **Paso 2: Actualizar Bookmarks**
- File Explorer favorites
- VSCode workspaces
- Terminal shortcuts

### **Paso 3: Configurar Backup Alternative**
- External drive backups
- Git remote repos
- Cloud storage para non-code files

---

## ✅ Beneficios Post-Remoción

### **Git Performance**:
- ✅ No más sync conflicts
- ✅ Faster git operations
- ✅ No file locking
- ✅ Reliable .git folder

### **System Performance**:
- ✅ Less CPU usage
- ✅ Less disk I/O
- ✅ Faster file operations

### **Developer Experience**:
- ✅ Predictable file behavior
- ✅ No surprise syncs
- ✅ Better control

---

## 📞 Soporte

Si tienes problemas durante la remoción:

1. **Stop y toma screenshot** del error
2. **No fuerces nada** que cause errores
3. **Verifica backup** antes de continuar
4. **Reinicia** si es necesario

---

## ⚠️ ADVERTENCIA FINAL

**Antes de ejecutar cualquier comando**:
1. ✅ Backup completo
2. ✅ Verificar MYORG_LOCAL
3. ✅ Cerrar todos los programas
4. ✅ Ejecutar como Administrador

**OneDrive removal es IRREVERSIBLE** - Una vez removido, todos los archivos en OneDrive folder serán borrados.

---

**¿Listo para proceder?**

Ejecuta: `.\find_snowsql_and_remove_onedrive.bat` para comenzar el análisis.
