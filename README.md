# Ungoogled Chromium Extensions Updater

Ungoogled Chromium extensions updater. This script is used to update Chromium extensions available and installed from Chrome Web Store.

## Dependencies

```
python3.6+
chromium
python-requests
wget
```

## Usage

1) Set Chromium flag `#extension-mime-request-handling` to **Always prompt for install**.

2) Run the script, eg.:
```
python ungoogled-chromium-extensions-updater.py
```

**Warning for Windows users**: On Windows, chocolatey packages [chrlauncher](https://chocolatey.org/packages/chrlauncher.portable) and [wget](https://chocolatey.org/packages/Wget) are expected to be installed. In any other case, please adjust the binary file paths and flags appropriately.