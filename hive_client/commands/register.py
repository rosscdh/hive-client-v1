# -*- coding: utf-8 -*-
from flask.ext.script import Command, Option

from ..services import BoxApiService


class Register(Command):
    option_list = (
        Option('--project', '-p',
               dest='project',
               default=None),
    )

    def run(self, **kwargs):
        """
        """
        s = BoxApiService()
        resp = s.register(**kwargs)

        print(resp.content)
