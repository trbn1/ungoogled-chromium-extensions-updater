import json
import os
import posixpath
import subprocess
import requests

from xdg.BaseDirectory import xdg_config_home

### ### ### ### ### ###
DOWNLOADER = '/usr/bin/wget'
BROWSER = '/usr/bin/chromium'
DL_LOCATION = '/tmp'
CONFIG_DIR = xdg_config_home
EXTENSIONS_PATH = CONFIG_DIR + '/chromium/Default/Extensions'
LOCAL_STATE_PATH = CONFIG_DIR + '/chromium/Local State'
MANIFEST_PATH_TEMPLATE = CONFIG_DIR + '/chromium/Default/Extensions/{id}/{version}/manifest.json'
LOCALE_PATH_TEMPLATE = CONFIG_DIR + '/chromium/Default/Extensions/{id}/{version}/_locales/{locale}/messages.json'
### ### ### ### ### ###

# https://ungoogled-software.github.io/ungoogled-chromium-wiki/faq#can-i-install-extensions-from-the-chrome-webstore
CRX_URL_TEMPLATE = 'https://clients2.google.com/service/update2/crx?response=redirect&acceptformat=crx2,crx3&prodversion={version}&x=id%3D{id}%26installsource%3Dondemand%26uc'


def get_installed_chromium_version():
    with open(LOCAL_STATE_PATH, 'rb') as file:
        data = json.load(file)

    return data['startup_metric']['last_startup_version']


def get_extension_ids():

    ids = set(os.listdir(EXTENSIONS_PATH))
    return ids - {'Temp'}


def get_installed_version(extension_id):
    versions = os.listdir(os.path.join(EXTENSIONS_PATH, extension_id))
    return sorted(versions, reverse=True)[0]


def check_for_update(chromium_version, extension_id, installed_version):
    crx_url = CRX_URL_TEMPLATE.format(version=chromium_version, id=extension_id)
    response = requests.get(crx_url, allow_redirects=False, stream=True)

    try:
        location = response.headers['Location']
    except KeyError:
        #print('Extension with id (' + extension_id + ') is not from webstore')
        return

    filename = posixpath.basename(location)
    version = os.path.splitext(filename)[0].replace('extension_', '', 1)
    if version.replace('_', '.') not in installed_version.replace('_', '.') and installed_version.replace('_', '.') not in version.replace('_', '.'):
        return version, location


def download_update(crx_path, name):
    executable = DOWNLOADER
    out = '--output-document=' + DL_LOCATION + '/' + name
    args = [executable, out, crx_path]
    
    subprocess.run(args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    

def install_update(name):
    executable = BROWSER
    crx_path = DL_LOCATION + '/' + name
    args = [executable, crx_path]
    
    subprocess.run(args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


def load_manifest(extension_id, version):
    path = MANIFEST_PATH_TEMPLATE.format(id=extension_id, version=version)
    with open(path, 'rb') as file:
        return json.load(file)


def load_locale(extension_id, version):
    try:
        path = LOCALE_PATH_TEMPLATE.format(id=extension_id, version=version, locale='en')
        with open(path, 'rb') as file:
            return json.load(file)
    except FileNotFoundError:
        path = LOCALE_PATH_TEMPLATE.format(id=extension_id, version=version, locale='en_US')
        with open(path, 'rb') as file:
            return json.load(file)


def main():
    chromium_version = get_installed_chromium_version()
    chromium_major_version = '.'.join(chromium_version.split('.', 2)[:-1])
    print(f'Detected Chromium version: {chromium_version} (Major: {chromium_major_version})')

    for extension_id in get_extension_ids():
        extension_version = get_installed_version(extension_id)
        manifest = load_manifest(extension_id, extension_version)
        ext_name = manifest['name']
        if '__MSG_' in manifest['name']:
            tmp = manifest['name']
            tmp = tmp.replace('__MSG_', '')
            tmp = tmp.replace('__', '')
            locale = load_locale(extension_id, extension_version)
            ext_name = locale[tmp]['message']

        curr_version = manifest['version']
        print(f'Checking updates for extension {ext_name!r} v{curr_version} ({extension_id})...')
        update = check_for_update(chromium_major_version, extension_id, extension_version)
        if not update:
            continue

        version, url = update
        print(f'Downloading update {version}: {url}...')
        name = ext_name + ' v' + version + '.crx'
        download_update(url, name)       
        
        print(f'Installing update...')
        install_update(name)     


if __name__ == '__main__':
    main()
