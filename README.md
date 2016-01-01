# publishstatic command

## Install

```bash
    pip install publishstatic
```


## Setup

Add `publishstatic` to INSTALLED_APPS:
```python
    INSTALLED_APPS = [
        ...
        'publishstatic',
    ]
```

Ensure the storage engine is set to use ManifestStaticFilesStoarge in `settings.py`

```python
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

Set you bucket/subdirectory name if needed.

```python
    PUBLISH_BUCKET_NAME = 'tracktor'
    PUBLISH_STORAGE_ENGINE = 's3'  # or 'local' for testing
```

Run the shell command to collect static.  Then publish!
```bash
    ./manage.py collectstatic
    ./manage.py publishstatic
```

That's it!