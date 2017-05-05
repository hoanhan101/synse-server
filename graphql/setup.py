"""
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""
VERSION = '0.1'

config = {
    'name': 'graphql_frontend',
    'version': VERSION,
    'author': 'Thomas Rampelberg',
    'author_email': 'thomasr@vapor.io',
    'test_suite': 'nose.collector'
}

if __name__ == '__main__':
    from setuptools import setup

    setup(**config)
