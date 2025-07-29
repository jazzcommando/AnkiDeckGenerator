@echo off
REM Change la page de code de la console en UTF-8 pour supporter les caracteres speciaux
chcp 65001 > nul

REM Les deux premiers chiffres/lettres controlent les couleurs :
REM Premier = fond, Deuxieme = texte
REM 0 = Noir, 1 = Bleu, 2 = Vert, 3 = Aigue-marine, 4 = Rouge, 5 = Violet, 6 = Jaune
REM 7 = Blanc, 8 = Gris, 9 = Bleu clair, A = Vert clair, B = Aigue-marine clair
REM C = Rouge clair, D = Violet clair, E = Jaune clair, F = Blanc vif
color 0A

set SCRIPT_DIR=%~dp0

echo.
echo *******************************************
echo   █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█
echo   █                                                 █
echo   █       ✨ THE ANKI IS UPDATING BABYYYYYYY        ✨   █
echo   █                                                 █
echo   █▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
echo *******************************************
echo.

REM beep boop bip bip beep boop
for /l %%i in (1,1,3) do (
    echo. . .
    timeout /t 0 /nobreak >nul
)
echo.

REM Checking pour VEnv python
IF EXIST "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    color 0B
    echo [INFO] VEnv Trouvé, activation...
    timeout /t 1 /nobreak >nul
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
    echo [INFO] Virtual environment activated!
    timeout /t 1 /nobreak >nul
) ELSE (
    color 0E
    echo [OOPSIE] Pas de VEnv sur ce PC, le script tournera directement sur Python
    timeout /t 2 /nobreak >nul
)
echo.

color 0F
echo [IT BEGINS] Lancement du generateur de deck...
timeout /t 1 /nobreak >nul
echo Si ca prend un moment, c'est parce qu'il a trop de fichiers WAV.
timeout /t 1 /nobreak >nul
echo. .
timeout /t 0 /nobreak >nul
echo. .
timeout /t 0 /nobreak >nul
echo. .
timeout /t 0 /nobreak >nul
echo mais c'est pas grave :)
timeout /t 1 /nobreak >nul
echo.

REM Barre de chargement simple (purement esthetique, ne reflete pas le vrai progres lol)
<nul set /p "=Progres: ["
for /l %%i in (1,1,20) do (
    <nul set /p "=^="  REM <-- CORRECTION ICI : ECHAPPER LE SIGNE =
    timeout /t 0 /nobreak >nul
)
echo "]"
timeout /t 1 /nobreak >nul
echo.

color 0A
REM Execute le script Python
REM La sortie du script Python (messages, erreurs, succes) sera affichee ici.
python "%SCRIPT_DIR%DeckGenerator.py"

echo.
echo *******************************************
color 0B
echo [SUCCES]
echo.
timeout /t 0 /nobreak >nul
echo.
timeout /t 1 /nobreak >nul
echo === ETAPE SUIVANTE ===
color 0F
timeout /t 1 /nobreak >nul
echo ===================NUMERO UNO: Lance Anki
echo.
timeout /t 0 /nobreak >nul
echo ===================NUMERO DOS: CLIQUE SUR Fichier - Importer...
echo.
timeout /t 0 /nobreak >nul
echo ===================NUMERO TRES: Selectionne le fichier apkg qui vient d'etre fait.
timeout /t 1 /nobreak >nul
echo ===================Anki mettra a jour les cartes existantes et ajoutera les nouvelles.
timeout /t 1 /nobreak >nul
echo *******************************************
timeout /t 1 /nobreak >nul
echo ===================Et surtout, le progres d'apprentissage est preserve (assez important)
echo.
color 0A
echo *******************************************

REM Desactive l'environnement virtuel si vous l'avez active
IF EXIST "%SCRIPT_DIR%venv\Scripts\deactivate.bat" (
    color 07
    timeout /t 1 /nobreak >nul
    call "%SCRIPT_DIR%venv\Scripts\deactivate.bat"
    timeout /t 1 /nobreak >nul
)

echo.
color 07
echo ===================Processus fini. GOOD ENGLANDO.===================
echo (tu peux appuyer sur n'importe quelle touche pour fermer ça maintenant btw)
pause