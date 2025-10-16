## Getting started and Authentication[¶](#getting-started-and-authentication "Permalink to this heading")

The PythonAnywhere API uses token-based authentication. You can get your token from [your Account page on the API Token tab](https://www.pythonanywhere.com/account/#api_token).

It's used in a header called `Authorization`, and the value is encoded as the string "Token", followed by a space, followed by your token, like this:

'Authorization': 'Token {}'.format(token)

For example, this code using the `requests` module would get the details of your CPU usage on PythonAnywhere; you would just need to change the three variables at the top to match your actual username, your API token, and the correct host:

- `www.pythonanywhere.com` if your account is on our US-based system.
- `eu.pythonanywhere.com` if your account is on our EU-based system.

import requests
username \= 'your username'
token \= 'your token'
host \= 'your host'

response \= requests.get(
    'https://{host}/api/v0/user/{username}/cpu/'.format(
        host\=host, username\=username
    ),
    headers\={'Authorization': 'Token {token}'.format(token\=token)}
)
if response.status_code \== 200:
    print('CPU quota info:')
    print(response.content)
else:
    print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))

Once you've generated your token, you can copy and paste it for use in your scripts. You can also access it at any time from PythonAnywhere consoles, webapps and tasks in a pre-populated environment variable, `$API_TOKEN`.

You will need to reload your webapp and start new consoles for this environment variable to be in place.

## Endpoints[¶](#endpoints "Permalink to this heading")

All endpoints are hosted at *https://www.pythonanywhere.com/* or *https://eu.pythonanywhere.com/* depending on where your account is registered.

## Rate-limits[¶](#rate-limits "Permalink to this heading")

Each endpoint has a 40 requests per minute rate limit, apart from the `send_input` endpoint on consoles, which is 120 requests per minute.

### Always_On[¶](#always_on "Permalink to this heading")

#### /api/v0/user/{username}/always_on/[¶](#apiv0userusernamealways_on "Permalink to this heading")

| Method | Description                           | Parameters                    |
| ------ | ------------------------------------- | ----------------------------- |
| GET    | List all of your always-on tasks      | (no parameters)               |
| POST   | Create and start a new always-on task | command, description, enabled |

#### /api/v0/user/{username}/always_on/{id}/[¶](#apiv0userusernamealways_onid "Permalink to this heading")

| Method | Description                                 | Parameters                    |
| ------ | ------------------------------------------- | ----------------------------- |
| GET    | Return information about an always-on task. | (no parameters)               |
| PUT    | Endpoints for always-on tasks               | command, description, enabled |
| PATCH  | Endpoints for always-on tasks               | command, description, enabled |
| DELETE | Stop and delete an always-on task           | (no parameters)               |

#### /api/v0/user/{username}/always_on/{id}/restart/[¶](#apiv0userusernamealways_onidrestart "Permalink to this heading")

| Method | Description                   | Parameters                    |
| ------ | ----------------------------- | ----------------------------- |
| POST   | Endpoints for always-on tasks | command, description, enabled |

### Consoles[¶](#consoles "Permalink to this heading")

#### /api/v0/user/{username}/consoles/[¶](#apiv0userusernameconsoles "Permalink to this heading")

| Method | Description                                                                                                                     | Parameters                               |
| ------ | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| GET    | List all your consoles                                                                                                          | (no parameters)                          |
| POST   | Create a new console object (NB does not actually start the process. Only connecting to the console in a browser will do that). | executable, arguments, working_directory |

#### /api/v0/user/{username}/consoles/shared_with_you/[¶](#apiv0userusernameconsolesshared_with_you "Permalink to this heading")

| Method | Description                    | Parameters      |
| ------ | ------------------------------ | --------------- |
| GET    | View consoles shared with you. | (no parameters) |

#### /api/v0/user/{username}/consoles/{id}/[¶](#apiv0userusernameconsolesid "Permalink to this heading")

| Method | Description                                  | Parameters      |
| ------ | -------------------------------------------- | --------------- |
| GET    | Return information about a console instance. | (no parameters) |
| DELETE | Kill a console.                              | (no parameters) |

#### /api/v0/user/{username}/consoles/{id}/get_latest_output/[¶](#apiv0userusernameconsolesidget_latest_output "Permalink to this heading")

| Method | Description                                                                 | Parameters      |
| ------ | --------------------------------------------------------------------------- | --------------- |
| GET    | Get the most recent output from the console (approximately 500 characters). | (no parameters) |

#### /api/v0/user/{username}/consoles/{id}/send_input/[¶](#apiv0userusernameconsolesidsend_input "Permalink to this heading")

| Method | Description                                      | Parameters            |
| ------ | ------------------------------------------------ | --------------------- |
| POST   | "type" into the console. Add a "\\n" for return. | POST parameter: input |

### Cpu[¶](#cpu "Permalink to this heading")

#### /api/v0/user/{username}/cpu/[¶](#apiv0userusernamecpu "Permalink to this heading")

| Method | Description                                                                                                                                                                                                         | Parameters      |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| GET    | Returns information about cpu usage in json format:<br><br>{<br>    "daily_cpu_limit_seconds": &lt;int&gt;,<br>    "next_reset_time": &lt;isoformat&gt;,<br>    "daily_cpu_total_usage_seconds": &lt;float&gt;<br>} | (no parameters) |

### Databases[¶](#databases "Permalink to this heading")

#### /api/v0/user/{username}/databases/mysql/[¶](#apiv0userusernamedatabasesmysql "Permalink to this heading")

| Method | Description | Parameters      |
| ------ | ----------- | --------------- |
| GET    |             | (no parameters) |

### Default_Python3_Version[¶](#default_python3_version "Permalink to this heading")

#### /api/v0/user/{username}/default_python3_version/[¶](#apiv0userusernamedefault_python3_version "Permalink to this heading")

| Method | Description                                                                                                                                                                                                        | Parameters      |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| GET    | Returns information about user's current and available default Python 3 version in json format:<br><br>{<br>    "default_python3_version": &lt;str&gt;,<br>    "available_python3_versions": \[&lt;str&gt;\],<br>} | (no parameters) |
| PATCH  | Sets default Python 3 version for user.                                                                                                                                                                            | (no parameters) |

### Default_Python_Version[¶](#default_python_version "Permalink to this heading")

#### /api/v0/user/{username}/default_python_version/[¶](#apiv0userusernamedefault_python_version "Permalink to this heading")

| Method | Description                                                                                                                                                                                                    | Parameters      |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| GET    | Returns information about user's current and available default Python version in json format:<br><br>{<br>    "default_python_version": &lt;str&gt;,<br>    "available_python_versions": \[&lt;str&gt;\],<br>} | (no parameters) |
| PATCH  | Sets default Python version for user.                                                                                                                                                                          | (no parameters) |

### Default_Save_And_Run_Python_Version[¶](#default_save_and_run_python_version "Permalink to this heading")

#### /api/v0/user/{username}/default_save_and_run_python_version/[¶](#apiv0userusernamedefault_save_and_run_python_version "Permalink to this heading")

| Method | Description                                                                                                                                                                                                                                                  | Parameters      |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| GET    | Returns information about user's current and available Python version used for the "Run" button in the editor, in json format:<br><br>{<br>    "default_save_and_run_python_version": &lt;str&gt;,<br>    "available_python_versions": \[&lt;str&gt;\],<br>} | (no parameters) |
| PATCH  | Sets Python version used for the "Run" button in the editor.                                                                                                                                                                                                 | (no parameters) |

### Files[¶](#files "Permalink to this heading")

#### /api/v0/user/{username}/files/path{path}[¶](#apiv0userusernamefilespathpath "Permalink to this heading")

| Method | Description                                                                                                                                                                                                                                                                                                                                                                                       | Parameters      |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| GET    |                                                                                                                                                                                                                                                                                                                                                                                                   | (no parameters) |
| POST   | Uploads a file to the specified file path. Contents should be in a multipart-encoded file with the name "content". The attached filename is ignored. If the directories in the given path do not exist, they will be created. Any file already present at the specified path will be overwritten. Returns 201 on success if a file has been created, or 200 if an existing file has been updated. | (no parameters) |
| DELETE | Deletes the file at the specified path. This method can be used to delete log files that are not longer required. Returns 204 on success.                                                                                                                                                                                                                                                         | (no parameters) |

#### /api/v0/user/{username}/files/sharing/[¶](#apiv0userusernamefilessharing "Permalink to this heading")

| Method | Description                                                                      | Parameters           |
| ------ | -------------------------------------------------------------------------------- | -------------------- |
| POST   | Start sharing a file. Returns 201 on success, or 200 if file was already shared. | POST parameter: path |

#### /api/v0/user/{username}/files/sharing/?path={path}[¶](#apiv0userusernamefilessharingpathpath "Permalink to this heading")

| Method | Description                                                                | Parameters            |
| ------ | -------------------------------------------------------------------------- | --------------------- |
| GET    | Check sharing status for a path. Returns 404 if path not currently shared. | Query parameter: path |
| DELETE | Stop sharing a path. Returns 204 on successful unshare.                    | Query parameter: path |

#### /api/v0/user/{username}/files/tree/?path={path}[¶](#apiv0userusernamefilestreepathpath "Permalink to this heading")

| Method | Description                                                                                                                                             | Parameters            |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| GET    | Returns a list of the contents of a directory, and its subdirectories as a list. Paths ending in slash/ represent directories. Limited to 1000 results. | Query parameter: path |

### Schedule[¶](#schedule "Permalink to this heading")

#### /api/v0/user/{username}/schedule/[¶](#apiv0userusernameschedule "Permalink to this heading")

| Method | Description                      | Parameters                                            |
| ------ | -------------------------------- | ----------------------------------------------------- |
| GET    | List all of your scheduled tasks | (no parameters)                                       |
| POST   | Create a new scheduled task      | command, enabled, interval, hour, minute, description |

#### /api/v0/user/{username}/schedule/{id}/[¶](#apiv0userusernamescheduleid "Permalink to this heading")

| Method | Description                                | Parameters                                            |
| ------ | ------------------------------------------ | ----------------------------------------------------- |
| GET    | Return information about a scheduled task. | (no parameters)                                       |
| PUT    | Endpoints for scheduled tasks              | command, enabled, interval, hour, minute, description |
| PATCH  | Endpoints for scheduled tasks              | command, enabled, interval, hour, minute, description |
| DELETE | Delete an scheduled task                   | (no parameters)                                       |

### Students[¶](#students "Permalink to this heading")

#### /api/v0/user/{username}/students/[¶](#apiv0userusernamestudents "Permalink to this heading")

| Method | Description                                                                                                                                                                                   | Parameters      |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| GET    | Returns a list of students of the current user<br><br>{<br>    "students": \[<br>        {"username": &lt;string&gt;},<br>        {"username": &lt;string&gt;},<br>        ...<br>    \]<br>} | (no parameters) |

#### /api/v0/user/{username}/students/{student}/[¶](#apiv0userusernamestudentsstudent "Permalink to this heading")

| Method | Description | Parameters      |
| ------ | ----------- | --------------- |
| DELETE |             | (no parameters) |

### System_Image[¶](#system_image "Permalink to this heading")

#### /api/v0/user/{username}/system_image/[¶](#apiv0userusernamesystem_image "Permalink to this heading")

| Method | Description                                                                                                                                                                               | Parameters      |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| GET    | Returns information about user's current and available system images in json format:<br><br>{<br>    "system_image": &lt;str&gt;,<br>    "available_system_images": \[&lt;str&gt;\],<br>} | (no parameters) |
| PATCH  | Sets system image for user.                                                                                                                                                               | (no parameters) |

### Webapps[¶](#webapps "Permalink to this heading")

#### /api/v0/user/{username}/webapps/[¶](#apiv0userusernamewebapps "Permalink to this heading")

| Method | Description                                                                                          | Parameters                                   |
| ------ | ---------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| GET    | List all webapps                                                                                     | (no parameters)                              |
| POST   | Create a new webapp with manual configuration. Use (for example) "python310" to specify Python 3.10. | POST parameters: domain_name, python_version |

#### /api/v0/user/{username}/webapps/{domain_name}/[¶](#apiv0userusernamewebappsdomain_name "Permalink to this heading")

| Method | Description                                                                                                        | Parameters                                                                                                                                              |
| ------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | Return information about a web app's configuration                                                                 | (no parameters)                                                                                                                                         |
| PUT    | Modify configuration of a web app. (NB a reload is usually required to apply changes).                             | python_version, source_directory, virtualenv_path, force_https, password_protection_enabled, password_protection_username, password_protection_password |
| PATCH  | Modify configuration of a web app. (NB a reload is usually required to apply changes).                             | python_version, source_directory, virtualenv_path, force_https, password_protection_enabled, password_protection_username, password_protection_password |
| DELETE | Delete the webapp. This will take the site offline. Config is backed up in /var/www, and your code is not touched. | (no parameters)                                                                                                                                         |

#### /api/v0/user/{username}/webapps/{domain_name}/disable/[¶](#apiv0userusernamewebappsdomain_namedisable "Permalink to this heading")

| Method | Description         | Parameters            |
| ------ | ------------------- | --------------------- |
| POST   | Disable the webapp. | POST parameters: none |

#### /api/v0/user/{username}/webapps/{domain_name}/enable/[¶](#apiv0userusernamewebappsdomain_nameenable "Permalink to this heading")

| Method | Description        | Parameters            |
| ------ | ------------------ | --------------------- |
| POST   | Enable the webapp. | POST parameters: none |

#### /api/v0/user/{username}/webapps/{domain_name}/reload/[¶](#apiv0userusernamewebappsdomain_namereload "Permalink to this heading")

| Method | Description                                                                       | Parameters            |
| ------ | --------------------------------------------------------------------------------- | --------------------- |
| POST   | Reload the webapp to reflect changes to configuration and/or source code on disk. | POST parameters: none |

#### /api/v0/user/{username}/webapps/{domain_name}/ssl/[¶](#apiv0userusernamewebappsdomain_namessl "Permalink to this heading")

| Method | Description                                                                                                                                                                                                                                       | Parameters                                                                                                                                              |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | Get and set TLS/HTTPS info. POST parameters to the right are incorrect, use \`cert\` and \`private_key\` when posting.<br><br>POST {'cert_type': 'letsencrypt-auto-renew'} to this endpoint to enable an auto-renewing Let's Encrypt certificate. | (no parameters)                                                                                                                                         |
| POST   | Get and set TLS/HTTPS info. POST parameters to the right are incorrect, use \`cert\` and \`private_key\` when posting.<br><br>POST {'cert_type': 'letsencrypt-auto-renew'} to this endpoint to enable an auto-renewing Let's Encrypt certificate. | python_version, source_directory, virtualenv_path, force_https, password_protection_enabled, password_protection_username, password_protection_password |
| DELETE | Get and set TLS/HTTPS info. POST parameters to the right are incorrect, use \`cert\` and \`private_key\` when posting.<br><br>POST {'cert_type': 'letsencrypt-auto-renew'} to this endpoint to enable an auto-renewing Let's Encrypt certificate. | (no parameters)                                                                                                                                         |

#### /api/v0/user/{username}/webapps/{domain_name}/static_files/[¶](#apiv0userusernamewebappsdomain_namestatic_files "Permalink to this heading")

| Method | Description                                                  | Parameters      |
| ------ | ------------------------------------------------------------ | --------------- |
| GET    | List all the static files mappings for a domain.             | (no parameters) |
| POST   | Create a new static files mapping. (webapp restart required) | url, path       |

#### /api/v0/user/{username}/webapps/{domain_name}/static_files/{id}/[¶](#apiv0userusernamewebappsdomain_namestatic_filesid "Permalink to this heading")

| Method | Description                                              | Parameters      |
| ------ | -------------------------------------------------------- | --------------- |
| GET    | Get URL and path of a particular mapping.                | (no parameters) |
| PUT    | Modify a static files mapping. (webapp restart required) | url, path       |
| PATCH  | Modify a static files mapping. (webapp restart required) | url, path       |
| DELETE | Remove a static files mapping. (webapp restart required) | (no parameters) |

#### /api/v0/user/{username}/webapps/{domain_name}/static_headers/[¶](#apiv0userusernamewebappsdomain_namestatic_headers "Permalink to this heading")

| Method | Description                                           | Parameters       |
| ------ | ----------------------------------------------------- | ---------------- |
| GET    | List all the static headers for a domain.             | (no parameters)  |
| POST   | Create a new static header. (webapp restart required) | url, name, value |

#### /api/v0/user/{username}/webapps/{domain_name}/static_headers/{id}/[¶](#apiv0userusernamewebappsdomain_namestatic_headersid "Permalink to this heading")

| Method | Description                                       | Parameters       |
| ------ | ------------------------------------------------- | ---------------- |
| GET    | Get URL, name and value of a particular header.   | (no parameters)  |
| PUT    | Modify a static header. (webapp restart required) | url, name, value |
| PATCH  | Modify a static header. (webapp restart required) | url, name, value |
| DELETE | Remove a static header. (webapp restart required) | (no parameters)  |

### Websites[¶](#websites "Permalink to this heading")

#### /api/v1/user/{username}/websites[¶](#apiv1userusernamewebsites "Permalink to this heading")

| Method | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Parameters                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| POST   | Create a new domain and associated webapp Returns information about created website (domain with webapp) in json format:<br><br>{<br>    'id': &lt;int&gt;,<br>    'user': &lt;str&gt;,<br>    'domain_name': &lt;str&gt;,<br>    'enabled': &lt;bool&gt;,<br>    'webapp': {<br>        'id': &lt;str&gt;,<br>        'command': &lt;str&gt;,<br>        'domains': \[{'domain_name': &lt;str&gt;, 'enabled': &lt;bool&gt;}\]<br>    },<br>    'logfiles': {<br>        'access': &lt;str&gt;,<br>        'server': &lt;str&gt;,<br>        'error': &lt;str&gt;,<br>    }<br>}<br><br>`logfiles` paths are ready to be used in the `files` API | domain_name, enabled, webapp |

#### /api/v1/user/{username}/websites/[¶](#apiv1userusernamewebsites_1 "Permalink to this heading")

| Method | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Parameters                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| GET    | List all domains with their webapp details in json format:<br><br>\[<br>    {<br>        'id': &lt;int&gt;,<br>        'user': &lt;str&gt;,<br>        'domain_name': &lt;str&gt;,<br>        'enabled': &lt;bool&gt;,<br>        'webapp': {<br>            'id': &lt;str&gt;,<br>            'command': &lt;str&gt;,<br>            'domains': \[{'domain_name': &lt;str&gt;, 'enabled': &lt;bool&gt;}\]<br>        },<br>        'logfiles': {<br>            'access': &lt;str&gt;,<br>            'server': &lt;str&gt;,<br>            'error': &lt;str&gt;,<br>        }<br>    }<br>\]                                                   | (no parameters)              |
| POST   | Create a new domain and associated webapp Returns information about created website (domain with webapp) in json format:<br><br>{<br>    'id': &lt;int&gt;,<br>    'user': &lt;str&gt;,<br>    'domain_name': &lt;str&gt;,<br>    'enabled': &lt;bool&gt;,<br>    'webapp': {<br>        'id': &lt;str&gt;,<br>        'command': &lt;str&gt;,<br>        'domains': \[{'domain_name': &lt;str&gt;, 'enabled': &lt;bool&gt;}\]<br>    },<br>    'logfiles': {<br>        'access': &lt;str&gt;,<br>        'server': &lt;str&gt;,<br>        'error': &lt;str&gt;,<br>    }<br>}<br><br>`logfiles` paths are ready to be used in the `files` API | domain_name, enabled, webapp |

#### /api/v1/user/{username}/websites/{domain_name}/[¶](#apiv1userusernamewebsitesdomain_name "Permalink to this heading")

| Method | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Parameters                   |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| GET    | Get information about the domain and its webapp in json format:<br><br>{<br>    'id': &lt;int&gt;,<br>    'user': &lt;str&gt;,<br>    'domain_name': &lt;str&gt;,<br>    'enabled': &lt;bool&gt;,<br>    'webapp': {<br>        'id': &lt;str&gt;,<br>        'command': &lt;str&gt;,<br>        'domains': \[{'domain_name': &lt;str&gt;, 'enabled': &lt;bool&gt;}\]<br>    },<br>    'logfiles': {<br>        'access': &lt;str&gt;,<br>        'server': &lt;str&gt;,<br>        'error': &lt;str&gt;,<br>    }<br>}<br><br>`logfiles` paths are ready to be used in the `files` API | (no parameters)              |
| PATCH  | Modify the domain/webapp                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | domain_name, enabled, webapp |
| DELETE | Remove the domain and webapp                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | (no parameters)              |

#### /api/v1/user/{username}/websites/{domain_name}/reload/[¶](#apiv1userusernamewebsitesdomain_namereload "Permalink to this heading")

| Method | Description                                                                       | Parameters            |
| ------ | --------------------------------------------------------------------------------- | --------------------- |
| POST   | Reload the webapp to reflect changes to configuration and/or source code on disk. | POST parameters: none |