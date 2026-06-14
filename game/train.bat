title Projet NSI - Entraiment des IAs

echo off

echo ------------------------------
echo.
echo PROGRAMME D'ENTRAINEMENT DES IAS
echo Apres un nombre de generations definies dans le code, le cerveau genere sera sauvegarde.
echo Vous pourrez alors lancer le jeu normal et ces cerveaux entraines seront effectifs.
echo Entre chaque redemarrage de ce programme, le cerveau dejà sauvegarde est supprime.
echo.
echo ------------------------------
echo.

:start
python code/AISelection.py

PAUSE

goto start