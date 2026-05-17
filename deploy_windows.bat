@echo off
echo ====================================
echo [DEPLOY] BERNAS-AGENT - SQUARE CLOUD
echo ====================================
echo.

echo [INFO] Para Windows, use os comandos abaixo:
echo.
echo 1. Primeiro faça login:
echo    C:\Users\Carlos\AppData\Roaming\npm\squarecloud.cmd auth login
echo.
echo 2. Crie o pacote ZIP:
echo    python scripts\deploy_squarecloud.py
echo.
echo 3. Faça o deploy:
echo    C:\Users\Carlos\AppData\Roaming\npm\squarecloud.cmd upload bernas-agent-deploy.zip --name bernas-agent
echo.
echo [INFO] Ou execute manualmente:
echo.
echo Passo 1: cd C:\Users\Carlos\AppData\Roaming\npm
echo Passo 2: squarecloud.cmd auth login
echo Passo 3: cd C:\Users\Carlos\bernas-agent
echo Passo 4: python scripts\deploy_squarecloud.py
echo Passo 5: squarecloud.cmd upload bernas-agent-deploy.zip --name bernas-agent
echo.
echo [INFO] Seu bot local já está rodando:
echo Dashboard: http://localhost:8080/dashboard
echo Controle: http://localhost:8080/control
echo.
pause