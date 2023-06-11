#!/bin/sh

VERSION_NUMBER=$1 # for example 0.1
GIT_TAG=v${VERSION_NUMBER}

echo "ANKI_VOCABAI_VERSION='${VERSION_NUMBER}'" > addon/version.py
git commit -a -m "upgraded version to ${VERSION_NUMBER}"
git push
git tag -a ${GIT_TAG} -m "version ${GIT_TAG}"
git push origin ${GIT_TAG}

# create .addon file
# remove meta.json, which contains private key
rm meta.json
rm -rf __pycache__
ADDON_FILENAME=${HOME}/anki-addons-releases/anki-vocabai-${VERSION_NUMBER}.ankiaddon
zip --exclude "*node_modules*" "*__pycache__*" "test_*.py" "*test_services*" "*.ini" "*.workspace" "*.md" "*.sh" requirements.txt "*.code-workspace" "web" -r ${ADDON_FILENAME} *

# sync 
rclone sync ~/anki-addons-releases/ dropbox:Anki/anki-addons-releases/

# if you need to undo a release:
# git tag -d v0.2
# git push --delete origin v0.2
