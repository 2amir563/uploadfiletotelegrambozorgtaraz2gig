#!/bin/bash

# Update va nasbe pish-niyaz ha
sudo apt update && sudo apt install -y python3 python3-pip python3-venv aria2 p7zip-full curl

# Sakhte mohite majazi (venv)
python3 -m venv venv
source venv/bin/activate

# Nasbe library haye python
pip install --upgrade pip
pip install -r requirements.txt

# Gereftane اطلاعات az karbar
if [ -z "$API_ID" ]; then
    read -p "Enter API_ID: " API_ID_VAL
    export API_ID=$API_ID_VAL
fi

if [ -z "$API_HASH" ]; then
    read -p "Enter API_HASH: " API_HASH_VAL
    export API_HASH=$API_HASH_VAL
fi

if [ -z "$BOT_TOKEN" ]; then
    read -p "Enter BOT_TOKEN: " BOT_TOKEN_VAL
    export BOT_TOKEN=$BOT_TOKEN_VAL
fi

# Ejraye bot
echo "🚀 Dar hale shoroo'e bot..."
python3 bot.py
