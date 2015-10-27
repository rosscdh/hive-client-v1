#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from hive_client import app
from hive_client.commands import Workers, Register, UpdatePlaylist

manager = Manager(app)

manager.add_command('workers', Workers())
manager.add_command('assets', ManageAssets())
manager.add_command('register', Register())
manager.add_command('update_playlist', UpdatePlaylist())

if __name__ == "__main__":
    manager.run()
