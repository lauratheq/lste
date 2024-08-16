#!/usr/bin/python3

"""
This module provides functionality for monitoring changes in a specified directory
and triggering site updates in response to file changes.

The primary functions include:
- `setup_filestack`: Initializes or updates a stack of files and their modification times for monitoring.
- `run_file_watcher`: Continuously monitors files for changes and triggers site rendering and updating processes when changes are detected.

Usage:
    - Call `setup_filestack(lste)` to populate the file stack with current files and their modification times.
    - Call `run_file_watcher(lste)` to start watching the files and perform site updates when changes are detected.

The `lste` object is expected to have:
    - `base_path`: The root directory to watch for file changes.
    - `file_stack`: A dictionary to store file paths and their modification times.
    - Methods such as `load_templates`, `load_content`, `render_site`, and `save_site` for handling site rendering and updating processes.
"""

import os
import time

def setup_filestack(lste):
    """
    Loads all files in the specified path into a stack to be watched for changes.

    This function populates the `lste.file_stack` dictionary with the paths and modification
    times of all files in `lste.base_path`. This stack will be used by the file watcher to
    detect changes.

    Parameters:
        lste (obj): The LSTE object, which should have `base_path` and `file_stack` attributes.

    Returns:
        None
    """
    # Create a list of all files in the base path
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(lste.base_path) for f in filenames]

    # Initialize or update the file stack with modification times
    for file in files:
        mtime = os.path.getmtime(file)
        lste.file_stack[file] = mtime

def run_file_watcher(lste):
    """
    Watches the specified path for file changes and triggers site rendering when changes are detected.

    This function continuously monitors the files in `lste.base_path` for changes by comparing
    modification times. If a change is detected, it calls methods to load templates and content,
    render the site, and save the output. The file stack is then updated to reflect the current state.

    Parameters:
        lste (obj): The LSTE object, which should have `base_path`, `file_stack`, and methods
                    like `load_templates`, `load_content`, `render_site`, and `save_site`.

    Returns:
        None
    """
    print(f'Watching folders in {lste.base_path} for changed files ...')

    while True:
        change_found = False

        # List all files in the base path
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(lste.base_path) for f in filenames]
        
        # Check if any files have changed or been deleted
        for file in files:
            mtime = os.path.getmtime(file)
            if file not in lste.file_stack or lste.file_stack[file] != mtime:
                change_found = True

        # Remove files that no longer exist
        for check_file in list(lste.file_stack):
            if not os.path.isfile(check_file):
                lste.file_stack.pop(check_file)
                change_found = True

        # If changes are detected, trigger site rendering
        if change_found:
            lste.load_templates()
            lste.load_content()
            lste.render_site()
            lste.save_site()
            setup_filestack(lste)  # Reinitialize the file stack with current modification times

        # Sleep for a short period before checking again
        time.sleep(500 / 1000)
