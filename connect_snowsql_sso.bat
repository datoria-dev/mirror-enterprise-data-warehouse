@echo off
REM Script para conectar a Snowflake usando SSO (Okta)
REM Configuracion basada en snowflake_config.json

echo ========================================
echo Conectando a Snowflake con SSO (Okta)
echo ========================================
echo.
echo Account: GenericCorp-CRH_EDW
echo User: fuad.onate@CompanyX.com
echo Warehouse: DEV_WH
echo Database: DEV_TRANSFORMATION
echo Schema: METADATA
echo Role: DEV_DEVELOPER
echo.
echo Se abrira una ventana del navegador para autenticacion...
echo.

"C:\Program Files\Snowflake SnowSQL\snowsql.exe" ^
  -a GenericCorp-CRH_EDW ^
  -u fuad.onate@CompanyX.com ^
  --authenticator externalbrowser ^
  -w DEV_WH ^
  -d DEV_TRANSFORMATION ^
  -s METADATA ^
  -r DEV_DEVELOPER

echo.
echo Conexion cerrada.
pause
