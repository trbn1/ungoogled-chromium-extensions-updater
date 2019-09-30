# Ungoogled Chromium Extensions Updater

Ungoogled Chromium extensions updater. This script is used to update Chromium extensions available and installed from Chrome Web Store.

## Dependencies

```
chromium
python-requests
python-xdg
wget
```

## Usage

1) Set Chromium flag `#extension-mime-request-handling` to **Always prompt for install**.

2) Run the script, eg.:
```
python ungoogled-chromium-extensions-updater.py
```