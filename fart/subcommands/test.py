# -*- coding: utf-8 -*-
from fart.commands import create

create("test", "tests your code", lambda parser: None, lambda _: 0)
