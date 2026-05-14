# config/config_manager.py

import json
import os

CONFIG_PATH = "tools_config.json"


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"rules": {}, "api_config": {}}

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_api_config():
    config = load_config()
    return config.get("api_config", {})


def save_api_config(api_config):

    config = load_config()
    config["api_config"] = api_config
    save_config(config)