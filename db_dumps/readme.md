1. To export the current state of the database to the `test_data.json` file, use the following command:
```commandline
python manage.py dumpdata --indent 2 > db_dumps/test_data.json
```

2. Then, to load the data from the `test_data.json` file into the database, use:
```commandline
python manage.py loaddata db_dumps/test_data.json
```

**To export / load data using certain database, specified in additional config settings file, use `--settings` option.**

Load data example, if another database connection details specified in `.../config/settings_local.py`:
```commandline
python manage.py loaddata db_dumps/test_data.json --settings=config.settings_local
```
