@echo off
echo Installation des dépendances...
pip install -r requirements.txt

echo.
echo Appuyez sur une touche pour continuer...
pause >nul

cls
echo Exécution du programme...
python main.py

echo.
echo Appuyez sur une touche pour quitter...
pause >nul
