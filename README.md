hive_client-client
============

Chute client the rasberry pi machines


1. git clone the repo
2. pip install -r requirements.txt
3. ./manage.py register -p :project_slug | (get the :project_slug from the main app.magnificent.com/project/:project_slug)
4. ./manage.py update_playlist           | (build the local playlist.json from the remote)
4. ./manage.py runserver -h 0.0.0.0 -p 5000                 | start the server
5. go to http://localhost:5000           | load the page
6. ./manage.py worker                    | to download the media locally