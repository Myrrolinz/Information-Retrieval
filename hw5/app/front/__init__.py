# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

from app import csrf

csrf = csrf

front = Blueprint("front", __name__)

from . import index,result_page,advanced_search,snapshot,suggest