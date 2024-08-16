# Home

This is a basic example for a LSTE project. Here we don't use any plugins and are just using the core functionalities of LSTE. Below you'll find a small documentation of the structure of this project.

## Config File

In the root folder of this example you find the `lste.conf` file. It contains the basic information of this website like the title, keywords and description.

```
[lste]
title = Example: Simple
keywords = lste, simple example
description = This is a very simple LSTE example
```

You can use these information throughout your project by placing `title`, `keywords` or `description` enclosed with `{{}}` in your templates or content.

## Templates & Assets

Templates define the layout and structure of your website. LSTE uses these templates to generate the final HTML pages. In this example, you will need the following template files:

* `index.html`: The base template where you can do whatever you want
* `page.html`: which represents the content of a single page

Templates use placeholders enclosed in `{{}}` to dynamically insert template parts. With `part: header.html` LSTE includes this template file.

### Assets

The assets directory contains static files such as CSS stylesheets, JavaScript files, and images that are used throughout your website and whatever you want. These assets will be copied to the ./dist directory during the site generation process.

## Content

Content files are where you define the actual text and media that will appear on your site. For this example, content is organized in the content directory. Here's what you might find:

* `index.md`: The main content file for the homepage
* `sample.md`: A page called sample :)

Each markdown file represents a `.html` file after the site generation.