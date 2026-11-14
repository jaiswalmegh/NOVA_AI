
import platform
import psutil
import subprocess


class SystemController:

    def get_system_info(self):

        return {
            "system": platform.system(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }

    def get_cpu_usage(self):

        return psutil.cpu_percent(interval=1)

    def get_ram_usage(self):

        memory = psutil.virtual_memory()

        return {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "used_gb": round(memory.used / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "usage_percent": memory.percent
        }

    def get_battery_status(self):

        battery = psutil.sensors_battery()

        if battery is None:
            return {
                "available": False,
                "message": "Battery information unavailable."
            }

        return {
            "available": True,
            "percentage": battery.percent,
            "plugged_in": battery.power_plugged
        }

    def lock_system(self):

        if platform.system() != "Windows":
            return False

        try:
            subprocess.Popen(
                ["rundll32.exe", "user32.dll,LockWorkStation"]
            )
            return True

        except OSError as error:
            print(f"System Lock Error: {error}")
            return False

    def get_disk_usage(self, path="C:\\"):

        try:
            disk = psutil.disk_usage(path)

            return {
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "used_gb": round(disk.used / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "usage_percent": disk.percent
            }

        except OSError as error:
            return {
                "error": str(error)
            }
