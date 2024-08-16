#!/usr/bin/python3

"""
LSTE - Lauras Simple Template Engine

This script is the main entry point for the LSTE project, a simple template engine that generates a static website
from templates, content, and assets. It provides functionality for both generating the website from scratch and 
watching for file changes to regenerate the website automatically.

Usage:
    ./lste.py [--watch] [--path=PATH]

Options:
    -p|--path   Sets the base directory for the website. Defaults to the current directory if not provided.
    -w|--watch  Enables automatic regeneration of the website when files change.

Description:
    This script reads configuration from `lste.conf` and `.lsterc`, initializes plugins and hooks, and then
    processes template files and content to generate the final website. It supports live-reloading if the
    `--watch` option is specified.

Legal Note:
    Written and maintained by Laura Herzog (laura-herzog@outlook.com)
    Licensed under the GPL license. See the project at https://github.com/lauratheq/lste
"""

import sys, os, getopt, shutil, time, re
import src.watcher as watcher
import src.helpers as helpers
from src.plugins import Plugins
from src.hooks import Hooks
import markdown

class LSTE:
    """
    Main LSTE Class for managing and generating a static website.

    Attributes:
        version (str): the current LSTE version
        base_path (str): The base directory for the website content.
        content_path (str): The directory containing content files.
        template_path (str): The directory containing template files.
        assets_path (str): The directory containing asset files.
        dist_path (str): The directory where the generated website is saved.
        templates (dict): A dictionary of loaded templates.
        content (dict): A dictionary of loaded content files.
        content_rendered (dict): Rendered content for each content file.
        rendered_html (dict): Final rendered HTML for each content file.
        prerendered_html (dict): HTML before applying custom functions.
        config_file (str): Path to the configuration file.
        file_stack (dict): A dictionary of files and their modification times.
        run_watcher (bool): Flag to indicate whether to run the file watcher.
        brackets_start (str): The start delimiter for template variables.
        brackets_end (str): The end delimiter for template variables.
        rcfile (ConfigParser): Configuration file object.
        hooks (Hooks): Hooks object for managing hooks.
        plugins (dict): Dictionary of loaded plugins.
        plugin_vars (dict): Variables for plugins.
        helpers (module): Module providing helper functions.

    Methods:
        __init__() -> None:
            Initializes the LSTE instance by setting up helpers, loading configuration files,
            initializing plugins, and loading templates and content. It starts the file watcher 
            if the `--watch` option is set, otherwise renders and saves the website.

        init_opts() -> None:
            Parses command-line options and sets the base directory for the website. Updates paths 
            based on the `--path` option if provided, and sets the `run_watcher` flag based on 
            the presence of the `--watch` option.

        load_templates() -> None:
            Loads all template files from the template directory into memory. Applies the 'templates' 
            hook to modify the loaded templates.

        load_content() -> None:
            Loads all content files from the content directory into memory. Extracts content, title, 
            and excerpt from each file. Applies the 'load_content' hook to modify the loaded content.

        render_site() -> None:
            Renders the website by applying templates and custom functions to the content. Processes 
            each content file, applies templates, and performs custom function replacements. 
            Applies the 'after_render_content' hook.

        load_template_file(template_file_name: str) -> str:
            Loads a template file and processes any included parts. Replaces template part references 
            within the content.

        load_template_parts(content: str) -> str:
            Loads and replaces template part references within a given template content.

        load_custom_functions(html: str) -> str:
            Applies custom functions to the rendered HTML, including setting the title, keywords, 
            description, and timestamp.

        save_site() -> None:
            Saves the rendered site content to the `dist` directory. Clears the directory, copies assets, 
            and writes HTML files for each rendered content item.
    """
    version = '0.2'
    
    base_path = os.getcwd()
    content_path = os.getcwd() + "/content"
    template_path = os.getcwd() + "/template"
    assets_path = os.getcwd() + "/assets"
    dist_path = os.getcwd() + "/dist"

    templates = {}
    content = {}
    content_rendered = {}
    rendered_html = {}
    prerendered_html = {}

    config_file = ""
    file_stack = {}
    run_watcher = False

    brackets_start = '{{'
    brackets_end = '}}'

    rcfile = None
    hooks = None
    plugins = {}
    plugin_vars = {}

    helpers = None

    def __init__(self) -> None:
        """
        Initializes the LSTE instance by setting up helpers, loading configuration files,
        initializing plugins, and loading templates and content. If the `--watch` option is set,
        it starts the file watcher; otherwise, it renders and saves the website.

        Returns:
            None
        """
        # set helpers
        self.helpers = helpers

        # get the opts
        self.init_opts()

        # if the user didn't provide a lste.conf for the project
        # we consider this run as failed and nothing will be called
        self.config_file = self.helpers.load_config(self.base_path + '/lste.conf')
        if self.config_file == False:
            print("No lste file found in this project.")
            sys.exit()

        # init the rcfile
        self.rcfile = self.helpers.load_config(f"{os.path.expanduser('~')}/.lsterc")

        # set basic modules
        self.hooks = Hooks()
        plugins = Plugins(self.rcfile)
        self.plugins = plugins.init_plugins(self)
        plugins.load_plugins(self)

        # first hook for the plugins here
        self = self.hooks.apply('plugins_loaded', self)

        # load all the needed data
        self.load_templates()
        self.load_content()

        if self.run_watcher:
            watcher.setup_filestack(self)
            watcher.run_file_watcher(self)
        else:
            self.render_site()
            self.save_site()

    def init_opts(self) -> None:
        """
        Parses command-line options and sets the base directory for the website.
        Sets the `run_watcher` flag based on the presence of the `--watch` option.
        Updates paths based on the `--path` option if provided.

        Returns:
            None
        """
        opts, args = getopt.getopt(sys.argv[1:], "hwp:", ["watch", "path="])
        for operator, argument in opts:
            if operator in ("-w", "--watch"):
                self.run_watcher = True
            elif operator in ("-p", "--path"):
                # make path absolute
                if os.path.isabs(argument) == False:
                    argument = os.path.abspath(argument)

                if os.path.isdir(argument):
                    self.base_path = argument
                    self.content_path = self.base_path + "/content"
                    self.template_path = self.base_path + "/template"
                    self.assets_path = self.base_path + "/assets"
                    self.dist_path = self.base_path + "/dist"
                else:
                    assert False, "directory does not exist"
            else:
                assert False, "unhandled option"

    def load_templates(self) -> None:
        """
        Loads all template files from the template directory into memory.
        Applies the 'templates' hook to modify the loaded templates.

        Returns:
            None
        """
        files = os.listdir(self.template_path)
        for file in files:
            filepath = self.template_path + '/' + file
            with open(filepath) as handle:
                content = handle.read()
            self.templates[file] = content

        self.templates = self.hooks.apply('templates', self.templates)

    def load_content(self) -> None:
        """
        Loads all content files from the content directory into memory.
        Extracts content, title, and excerpt from each file. Applies the 'load_content' hook 
        to modify the loaded content.

        Returns:
            None
        """
        files = os.listdir(self.content_path)
        for file in files:
            filepath = self.content_path + '/' + file

            # skip folders
            if os.path.isdir(filepath):
                continue

            with open(filepath) as handle:
                content = handle.read()

            # extract content
            self.content[file] = {}
            self.content[file]['content'] = content

            # excerpt
            self.content[file]['excerpt'] = self.helpers.extract_excerpt(content)

            # basic content
            content_pattern = r'^(#+)\s*(.*)$'
            self.content[file]['content'] = re.sub(content_pattern, '', content, count=1, flags=re.MULTILINE)
            self.content[file]['title'] = self.helpers.extract_title(content)

        self.content = self.hooks.apply('load_content', self.content, self)

    def render_site(self) -> None:
        """
        Renders the website by applying templates and custom functions to the content.
        It processes each content file, applies templates, and performs custom function replacements.
        It then applies the 'after_render_content' hook.

        Returns:
            None
        """
        # pre render
        for file in self.content:
            print(f'Rendering template for: {file}')

            # render the file content
            file_content = self.content[file]['content']

            # some content maybe doesn't want to have markdown enabled
            if 'skip_markdown' in self.content[file]:
                file_content_rendered = file_content
            else:
                file_content_rendered = markdown.markdown(file_content, extensions=['fenced_code', 'tables'])
            self.content_rendered[file] = file_content_rendered

            # load the base template and then recursively the parts
            self.prerendered_html[file] = self.load_template_file('index.html')

        # hook right before the custom functions which has potential
        # to overwrite certain template variables
        self = self.hooks.apply('pre_render_content', self)

        # render the prerendered_html with the builtin functions
        for file in self.prerendered_html:

            # set the template
            if 'template' in self.content[file]:
                single_template_file = self.templates[self.content[file]['template']]
            else:
                single_template_file = self.templates['page.html']

            # load the template
            single_content = single_template_file
            single_content = single_content.replace("{{title}}", self.content[file]['title'])
            single_content = single_content.replace("{{content}}", self.content_rendered[file])

            excerpt = self.hooks.apply('excerpt', self.content[file]['excerpt'], file, self)
            single_content = single_content.replace("{{excerpt}}", excerpt)
            
            single_content = self.hooks.apply('single_content', single_content, file, self)
            self.prerendered_html[file] = self.prerendered_html[file].replace("{{content}}", single_content)

            # hook right before the custom functions executes
            self.prerendered_html[file] = self.hooks.apply('pre_load_custom_functions', self.prerendered_html[file], file, self)

            # load the template functions
            self.rendered_html[file] = self.load_custom_functions(self.prerendered_html[file])
        
        # hook right after the custom functions which has potential
        # to overwrite certain template variables
        self = self.hooks.apply('after_render_content', self)

    def load_template_file(self, template_file_name) -> str:
        """
        Loads a template file and processes any included parts.

        Parameters:
            template_file_name (str): The filename of the template to load.

        Returns:
            str: The rendered HTML of the template.
        """
        template_content = self.templates[template_file_name]
        html = self.load_template_parts(template_content)
        return html

    def load_template_parts(self, content) -> str:
        """
        Loads and replaces template part references within a given template content.

        Parameters:
            content (str): The content of the template file.

        Returns:
            str: The rendered HTML with all template parts replaced.
        """
        html = content
        for line in content.splitlines():
            # load the template part
            line = line.lstrip()
            if "{{part: " in line:
                template_part = line.replace("{{part: ", "")
                template_part = template_part.replace("}}", "")
                template_part_filename = template_part
                part_content = self.load_template_file(template_part_filename)
                html = html.replace(f"{self.brackets_start}part: {template_part_filename}{self.brackets_end}", part_content)
        return html

    def load_custom_functions(self, html) -> str:
        """
        Applies custom functions to the rendered HTML, including setting the title, keywords,
        description, and timestamp.

        Parameters:
            html (str): The currently generated HTML.

        Returns:
            str: The manipulated HTML with custom functions applied.
        """
        # timestamp
        timestamp = int(time.time())
        html = html.replace('{{timestamp}}', str(timestamp))

        # replace config variables
        html = html.replace('{{title}}', self.config_file['lste']['title'])
        html = html.replace('{{keywords}}', self.config_file['lste']['keywords'])
        html = html.replace('{{description}}', self.config_file['lste']['description'])

        return html

    def save_site(self) -> None:
        """
        Saves the rendered site content to the `dist` directory. Clears the directory, copies assets,
        and writes HTML files for each rendered content item.

        Returns:
            None
        """
        # empty dist folder
        if os.path.isdir(self.dist_path):
            shutil.rmtree(self.dist_path)
        os.makedirs(self.dist_path)

        # copy assets folder
        shutil.copytree(self.assets_path, self.dist_path + '/assets')

        for filename in self.rendered_html:
            html_filename = filename.replace('.md', '.html')
            content = self.rendered_html[filename]
            content = content.lstrip()

            with open(f'{self.dist_path}/{html_filename}',"w") as handle:
                handle.write(content)
        
        self = self.hooks.apply('after_save_site', self)

''' Startup '''
if __name__ == '__main__':
    try:
        lste = LSTE()
    except KeyboardInterrupt:
        try:
            sys.exit(130)
        except SystemExit:
            sys.exit()
            os._exit(130)
