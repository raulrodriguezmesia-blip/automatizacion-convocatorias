@echo off
set /p GH_USER="Enter GitHub username: "
set /p GH_TOKEN="Enter GitHub token (or press Enter for SSH): "

echo Publishing automatizacion-convocatorias...
git remote add origin https://github.com/%GH_USER%/automatizacion-convocatorias.git
if "%GH_TOKEN%" neq "" (
    git remote set-url origin https://%GH_TOKEN%@github.com/%GH_USER%/automatizacion-convocatorias.git
)
git push -u origin main

echo Creating campaign-studio repository...
cd ..
git clone https://github.com/%GH_USER%/campaign-studio.git 2>nul || (
    echo Creating local repo for campaign-studio
    mkdir campaign-studio-temp
    robocopy %CD%\campaign-studio campaign-studio-temp /MIR
    cd campaign-studio-temp
    git init
    git add .
    git commit -m "Initial commit - Campaign Studio AI"
    git remote add origin https://github.com/%GH_USER%/campaign-studio.git
    if "%GH_TOKEN%" neq "" (
        git remote set-url origin https://%GH_TOKEN%@github.com/%GH_USER%/campaign-studio.git
    )
    git push -u origin main
)