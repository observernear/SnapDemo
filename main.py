#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

class SnapEnvironment:
    def __init__(self, logger):
        self.logger = logger

    def check_environment(self):
        self.logger.write_log("Checking if application is running in a Snap environment.")

        snap_vars = ['SNAP', 'SNAP_NAME', 'SNAP_REVISION', 'SNAP_ARCH']
        for var in snap_vars:
            value = os.environ.get(var, None)
            if value:
                self.logger.write_log(f"Environment variable {var}={value}")
            else:
                self.logger.write_log(f"Environment variable {var} not found.")

        self.logger.write_log("Checking connected Snap interfaces.")
        try:
            result = subprocess.run(["snap", "interfaces"], capture_output=True, text=True, check=True)
            self.logger.write_log(f"Snap interfaces:\n{result.stdout}")
        except Exception as e:
            self.logger.log_error(f"Error checking snap interfaces: {str(e)}")


class Logger:
    def __init__(self, log_path):
        self.log_path = os.path.join(os.environ.get('SNAP_USER_DATA', ''), 'log.txt')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        print(f"Logging to: {self.log_path}")

    def write_log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_path, 'a') as f:
            f.write(f"[{timestamp}] INFO: {message}\n")

    def log_error(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_path, 'a') as f:
            f.write(f"[{timestamp}] ERROR: {message}\n")

class FileSystemProbe:
    def __init__(self, logger):
        self.logger = logger

    def list_home_directory(self):
        self.logger.write_log("Listing contents of the home directory.")
        try:
            home = os.path.expanduser("~")
            files = os.listdir(home)
            self.logger.write_log(f"Home directory contains: {files}")
        except Exception as e:
            self.logger.log_error(f"Error accessing home directory: {str(e)}")

    def check_write_permission(self):
        self.logger.write_log("Checking write permissions in the home directory.")
        test_path = os.path.expanduser("~/snapdemo_testfile.txt")
        try:
            with open(test_path, 'w') as f:
                f.write("Snap confinement test.")
            os.remove(test_path)
            self.logger.write_log("Write permission to home directory is available.")
        except Exception as e:
            self.logger.log_error(f"Write permission check failed: {str(e)}")

    def perform_checks(self):
        self.list_home_directory()
        self.check_write_permission()

class AppConfig:
    def __init__(self):
        self.log_path = os.path.expanduser("~/log.txt")


class AppController:
    def __init__(self):
        self.config = AppConfig()
        self.logger = Logger(self.config.log_path)
        self.fs_probe = FileSystemProbe(self.logger)
        self.snap_env = SnapEnvironment(self.logger)

    def run(self):
        self.logger.write_log("SnapDemo started.")
        self.snap_env.check_environment()
        self.fs_probe.perform_checks()

        while True:
            choice = input("Enter 'r' to rerun checks, 'q' to quit: ").strip().lower()
            if choice == 'r':
                self.logger.write_log("Rerunning environment checks.")
                self.snap_env.check_environment()
                self.fs_probe.perform_checks()
            elif choice == 'q':
                self.logger.write_log("Exiting SnapDemo.")
                break
            else:
                self.logger.log_error("Invalid input received.")
                print("Invalid input. Please enter 'r' or 'q'.")


if __name__ == '__main__':
    app = AppController()
    app.run()
