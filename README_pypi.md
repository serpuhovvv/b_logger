# BLogger — Pytest Logging Plugin

### Full README.md available at [GitHub](https://github.com/serpuhovvv/b_logger)

- [Overview](#overview)
- [Report Examples](#report-examples)
- [Installation](#installation)
- [Setup](#setup)
  - [Project Name](#project_name)
  - [Time Zone](#timezone)
  - [Integrations](#integrations)
  - [Hide Passwords](#hide_passwords)
  - [Env and Base URL](#env-and-base_url)
- [BLogger API](#blogger-api)
---


## Overview

BLogger is a Pytest plugin for enhanced test logging and generating convenient and lightweight reports.  
It supports structured test steps, descriptions, info notes, known bugs, and automatic screenshots.  
Works seamlessly with Selenium WebDriver and Playwright Page instances. \
Integrates with Allure and Qase for fewer duplicates like .steps, .attach etc.
---


## Report Examples
Sample HTML reports and screenshots are available in the [GitHub repository](https://github.com/serpuhovvv/b_logger).

---



## Installation

```bash
pip install pytest-b-logger
```
---



## Setup
!!! Add ***blog.config.yaml*** file to the ***root*** of your project. !!!

### project_name
Bare minimum for everything to work is project_name: 
```yaml
project_name: 'Project Name'
```
Can be changed later via CLI when running tests
```bash
pytest --blog-project-name '...'
```


### timezone
Then you can set the desired Time Zone (IANA format e.g. Europe/Moscow, UTC, America/New_York).\
The list of available timezones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
```yaml
project_name: 'Project Name'

tz: 'Europe/Moscow'
```


### integrations
By default, integrations are turned off. \
If you are using Allure and want steps, info, description etc. to be duplicated to Allure, 
simply add integrations block and set ***allure: True***
```yaml
project_name: 'Project Name'

tz: 'Europe/Moscow'

integrations:
  allure: True
```


### hide_passwords
By default, passwords inside parameters are hidden.

If you want passwords to be shown simply set ***hide_passwords: False***
```yaml
project_name: 'Project Name'

tz: 'Europe/Moscow'

integrations:
  allure: True

hide_passwords: False
```


### env and base_url
You can add env and base url here.
```yaml
project_name: 'Project Name'

tz: 'Europe/Moscow'

integrations:
  allure: True

hide_passwords: True

env: 'prod' # optional
base_url: 'https://base-url.com' # optional
```
Which, could also be passed as command line options on test run, e.g. when using CI/CD:
```bash
pytest --blog-env 'prod' --blog-base-url 'https://base-url.com'
```

***!!! Note !!!*** Options apply in the following order: blog.config.yaml > blog methods inside code > Command Line Arguments 

Now you are all set up. \
Simply run pytest and ***b_logs*** folder will be generated 
with ***blog_report.html*** and ***blog_summary.html*** \
For more advanced usage please review ***[BLogger API](#blogger-api)***
---


## BLogger API

### Please see API Reference at [GitHub](https://github.com/serpuhovvv/b_logger)
