#!/usr/bin/python3

"""
This module provides the `Plugins` class for managing and loading plugins
into memory based on configuration provided by a `ConfigParser` object.

The `Plugins` class offers functionality to initialize plugins from a
specified configuration, load the plugins dynamically, and store them
for further use. The plugins are added to an internal dictionary and can
be accessed or managed through the class methods.

Usage:
    - Create an instance of the `Plugins` class with a `ConfigParser` object.
    - Call the `init_plugins` method to load and initialize plugins.
    - Call the `load_plugins` method to download and update plugins.
"""

import os
import importlib.util
import requests
import zipfile
from packaging import version
from typing import Dict, Any

class Plugins:
    """
    Manages the loading, initialization, and updating of plugins.

    This class handles dynamic loading of plugins from a configuration file,
    including downloading updates and installing them from remote repositories.

    Attributes:
        config_file (Optional[ConfigParser]): The configuration file object containing plugin details.
        plugins (Dict[str, Any]): A dictionary where keys are plugin names and values are the plugin modules.
        plugins_folder (str): The path to the folder where plugins are stored.

    Methods:
        __init__(config_file=None) -> None:
            Initializes the Plugins class with an optional configuration file object.
        init_plugins(lste) -> Dict[str, Any]:
            Initializes and loads plugins into memory based on the configuration.
            Returns a dictionary where keys are plugin names and values are the loaded plugin modules.
        load_plugins(lste) -> None:
            Downloads and updates plugins from their repositories based on the configuration.
        download_and_install_plugin(repo: str, local_plugin_path: str, latest_release: Dict[str, Any]) -> None:
            Downloads and installs or updates the plugin from the given repository using the latest release information.
    """
    config_file = None
    plugins: Dict[str, Any] = {}
    plugins_folder = os.path.expanduser("~/.local/share/lste/plugins")

    def __init__(self, config_file=None) -> None:
        """
        Initializes the Plugins class.

        Parameters:
            config_file (ConfigParser, optional): The configuration file object with plugin details.

        Returns:
            None
        """
        self.config_file = config_file
        self.plugins = {}

    def init_plugins(self, lste) -> Dict[str, Any]:
        """
        Initializes and loads plugins into memory.

        This method reads the plugin configuration from the provided `ConfigParser` object,
        dynamically loads the plugin modules, and stores them in the `self.plugins` dictionary.

        Parameters:
            lste (obj): The LSTE object used for plugin registration.

        Returns:
            Dict[str, Any]: A dictionary where keys are plugin names and values are the loaded plugin modules.
        """
        # Check if the configuration file is not present
        if not self.config_file:
            return {}
        
        # Check if the "plugins" section exists before retrieving its items
        if not self.config_file.has_section("plugins"):
            return {}

        # Retrieve the plugin items from the configuration
        plugin_items = self.config_file.items("plugins")
        if not plugin_items:
            return {}

        # Define the plugin folder path and ensure it exists
        plugins_folder = os.path.expanduser("~/.local/share/lste/plugins")
        os.makedirs(plugins_folder, exist_ok=True)

        # Initialize the plugins dictionary
        self.plugins.clear()  # Clear existing plugins if any

        # Iterate over each plugin item and load it
        for plugin_name, plugin_path in plugin_items:
            plugin_realpath = os.path.join(plugins_folder, plugin_name)
            plugin_file_realpath = os.path.join(plugin_realpath, f"{plugin_name}.py")

            # Check if the plugin configuration file exists
            plugin_config_location = os.path.join(plugin_realpath, "lste.conf")
            if not os.path.isfile(plugin_config_location):
                continue

            # Load the plugin module
            plugin_spec = importlib.util.spec_from_file_location(plugin_name, plugin_file_realpath)
            plugin = importlib.util.module_from_spec(plugin_spec)
            plugin_spec.loader.exec_module(plugin)

            # Add the plugin to the self.plugins dictionary
            self.plugins[plugin_name] = plugin
            
            # Call the register_hooks method if it exists
            if hasattr(plugin, 'register_hooks') and callable(getattr(plugin, 'register_hooks')):
                plugin.register_hooks(lste)
                print(f"Using plugin: {plugin_name}")

        return self.plugins
    
    def load_plugins(self, lste) -> None:
        """
        Downloads and updates plugins from their repositories.

        This method checks for each plugin's version in the local storage and compares it with the
        latest version available on GitHub. If an update is available, it downloads and installs
        the latest version of the plugin.

        Parameters:
            lste (obj): The LSTE object used for managing plugins and configuration.

        Returns:
            None
        """
        # Check if the "plugins" section exists before retrieving its items
        if not self.config_file.has_section("plugins"):
            return {}
        
        # Retrieve the plugin items from the configuration
        plugin_items = self.config_file.items("plugins")
        if not plugin_items:
            return
        
        # Parse the config_file to get the list of plugins and their repositories
        for plugin_name, repo in plugin_items:

            # Check if the plugin is already installed locally
            local_plugin_path = os.path.join(self.plugins_folder, plugin_name)
            local_version = None
            local_version_file = os.path.join(local_plugin_path, "lste.conf")

            if os.path.exists(local_version_file):
                local_config = lste.helpers.load_config(local_version_file)
                if 'lste' in local_config and 'version' in local_config['lste']:
                    local_version = local_config['lste']['version']

            # Step 4: Fetch the latest release version from GitHub
            github_api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            response = requests.get(github_api_url)
            if response.status_code != 200:
                continue

            response.raise_for_status()
            latest_release = response.json()
            remote_version = latest_release['tag_name']

            # Compare versions and update if necessary
            if local_version is None or version.parse(remote_version) > version.parse(local_version):
                print(f"Updating plugin {plugin_name} to version {remote_version}")
                # Download and install/update the plugin
                self.download_and_install_plugin(repo, local_plugin_path, latest_release)

    def download_and_install_plugin(self, repo: str, local_plugin_path: str, latest_release: Dict[str, Any]) -> None:
        """
        Downloads and installs or updates the plugin from the given repository using the latest release information.

        Parameters:
            repo (str): The repository name in the format 'owner/repo'.
            local_plugin_path (str): The local path where the plugin will be installed.
            latest_release (Dict[str, Any]): The latest release information including the zipball URL.

        Returns:
            None
        """
        # Implement the method to download and install the plugin from GitHub
        zip_url = latest_release['zipball_url']
        response = requests.get(zip_url)
        response.raise_for_status()

        # Create the plugin directory if it does not exist
        if not os.path.exists(local_plugin_path):
            os.makedirs(local_plugin_path)

        # Unzip the content to the local plugin path
        zip_path = os.path.join(local_plugin_path, "latest_release.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the top-level directory in the zip file
            top_level_dir = zip_ref.namelist()[0].split('/')[0]
            for member in zip_ref.infolist():
                # Skip the top-level directory itself
                if member.filename.startswith(top_level_dir):
                    # Extract everything under the top-level directory
                    extracted_path = os.path.join(local_plugin_path, os.path.relpath(member.filename, top_level_dir))
                    if member.is_dir():
                        os.makedirs(extracted_path, exist_ok=True)
                    else:
                        with open(extracted_path, 'wb') as extracted_file:
                            extracted_file.write(zip_ref.read(member.filename))

        os.remove(zip_path)
        print(f"Installed plugin {repo} to {local_plugin_path}")
