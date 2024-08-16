#!/usr/bin/python3

"""
This script contains several helper functions for processing text content and loading configurations.

The current functions included are:
- `extract_title`: Extracts the first title from the given content.
- `extract_excerpt`: Extracts the content following the first title up to the first double newline.
- `load_config`: Loads a configuration file and returns a config parser object.

Additional helper functions can be added to this file as needed.
"""

import re
import configparser
import os
from typing import Union

def extract_title(content: str) -> str:
    """
    Extracts the first title from the given content string. The title is defined as
    the first line that starts with one or more hash symbols (#) followed by text.

    Args:
        content (str): The content string from which to extract the title.

    Returns:
        str: The extracted title, or an empty string if no title is found.
    """
    # Define the pattern to match the first title
    title_pattern = r'^(#+)\s*(.*)$'
    
    # Find all titles
    title_matches = re.findall(title_pattern, content, re.MULTILINE)
    
    # Initialize title
    title = ''
    
    # If a title is found, extract it
    if title_matches:
        title = title_matches[0][1]
    
    return title

def extract_excerpt(content: str) -> str:
    """
    Extracts an excerpt from the given content string. The excerpt is defined as the content 
    following the first title (denoted by a line starting with '# ') up to the first double newline.

    Args:
        content (str): The content string from which to extract the excerpt.

    Returns:
        str: The extracted excerpt or the original content if no title is found.
    """
    # Define the pattern to match the first title and capture content after it up to the first double newline
    title_pattern = r'^# .*\n'
    content_pattern = r'((?:.*?(?:\n|$))+?)(?=\n\n|$)'
    
    # Find the first title
    title_match = re.search(title_pattern, content, re.MULTILINE)

    # Exit early if no title is found
    if not title_match:
        return content

    # The end index of the title match
    start_index = title_match.end()
    
    # Extract content after the title
    post_title_content = content[start_index:]
    
    # Find the first double newline after the title
    content_match = re.search(content_pattern, post_title_content, re.MULTILINE | re.DOTALL)
    
    if content_match:
        return content_match.group(1).strip()
    else:
        return content

def load_config(file: str) -> Union[configparser.ConfigParser, bool]:
    """
    Loads a configuration file and returns a config parser object.

    Args:
        file (str): The path to the configuration file.

    Returns:
        configparser.ConfigParser: The loaded configuration parser object.
        bool: False if the file does not exist.
    """
    # Check if the file exists
    if not os.path.isfile(file):
        return False

    # Read the file
    parser = configparser.ConfigParser()
    parser.read(file)

    return parser
