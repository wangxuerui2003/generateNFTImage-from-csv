rm generateNFTImages.exe
pyinstaller --onefile generateNFTImages.py && rm generateNFTImages.spec && rm -rf ./build && mv ./dist/generateNFTImages.exe . && rm -rf dist
