import unittest
import json
from flask import request, jsonify

from monolith.database import db, User, Story
from monolith.tests.mock_app import MockApp
from monolith.views.stories import _get_story
from monolith.app import create_app

class TestGetStory(unittest.TestCase):
    def test_get_story(self):
        app = create_app()
        app = app.test_client()

        #story found
        reply = app.get('/stories/1')
        data = str(reply.data, 'utf8')
        
        self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5></h5>\n    <ul>\n      \n      <li>\n      \"Trial story of example admin user :)\"    Likes: 42 (2019-10-24 12:22:20.016285)\n      \n      </li>\n      \n    </ul>\n  </body>\n</html>')

        #story not found
        reply = app.get('/stories/0')
        data = str(reply.data, 'utf8')
        
        self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5>story not found!</h5>\n    <ul>\n      \n    </ul>\n  </body>\n</html>')

        #invalid input
        reply = app.get('stories/ciao')
        data = str(reply.data, 'utf8')
        
        self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5>story not found!</h5>\n    <ul>\n      \n    </ul>\n  </body>\n</html>')