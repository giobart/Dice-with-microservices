from unittest import TestCase
from flask import request
from flask_login import current_user
import json

from monolith.app import create_app
from monolith.database import User


def test_follow_post(client, database, auth):
    reply = auth.login('test1', 'test1123')
    assert reply.status_code == 302

    reply = client.post('/users/1/follow')
    assert reply.status_code == 200
    assert reply.get_json()['message'] == 'User followed'

    reply = client.post('/users/3/follow')
    assert reply.status_code == 200
    assert reply.get_json()['message'] == 'User followed'

    user1 = database.session.query(User).filter_by(username='test1').one()
    assert len(user1.follows) == 2

    reply = client.post('/users/3/follow')
    assert reply.status_code == 200
    assert reply.get_json()['message'] == 'User followed'

    user1 = database.session.query(User).filter_by(username='test1').one()
    assert len(user1.follows) == 2

    reply = client.post('/users/5/follow')
    assert reply.status_code == 404
    assert reply.get_json()['error'] == 'User with id 5 does not exists'

    reply = client.post('/users/2/follow')
    assert reply.status_code == 400
    assert reply.get_json()['error'] == 'Cannot follow or unfollow yourself'


def test_follow_delete(client, database, auth):
    reply = auth.login('test1', 'test1123')
    assert reply.status_code == 302

    reply = client.post('/users/1/follow')
    assert reply.status_code == 200
    assert reply.get_json()['message'] == 'User followed'

    reply = client.post('/users/3/follow')
    assert reply.status_code == 200
    assert reply.get_json()['message'] == 'User followed'

    user1 = database.session.query(User).filter_by(username='test1').one()
    assert len(user1.follows) == 2

    reply = client.delete('/users/3/follow')
    assert reply.status_code == 200
    assert reply.get_json()['message'] == 'User unfollowed'

    user1 = database.session.query(User).filter_by(username='test1').one()
    assert len(user1.follows) == 1
    assert user1.follows[0].username == 'Admin'

    reply = client.delete('/users/3/follow')
    assert reply.status_code == 200
    assert reply.get_json()['message'] == 'User unfollowed'

    reply = client.delete('/users/5/follow')
    assert reply.status_code == 404
    assert reply.get_json()['error'] == 'User with id 5 does not exists'

    reply = client.post('/users/2/follow')
    assert reply.status_code == 400
    assert reply.get_json()['error'] == 'Cannot follow or unfollow yourself'


def test_followed_get(client, database, auth, templates):
    reply = auth.login('test1', 'test1123')
    assert reply.status_code == 302

    reply = client.post('/users/1/follow')
    assert reply.status_code == 200

    reply = client.post('/users/3/follow')
    assert reply.status_code == 200

    reply = client.get('/followed')
    assert reply.status_code == 200
    assert templates
    users = templates[-1]['users']
    assert len(users) == 2
    user1 = {'firstname': 'Admin', 'lastname': 'Admin', 'id': 1}
    user3 = {'firstname': 'First2', 'lastname': 'Last2', 'id': 3}
    assert users[0] == user1
    assert users[1] == user3

    reply = client.delete('/users/3/follow')
    assert reply.status_code == 200

    reply = client.get('/followed')
    assert reply.status_code == 200
    assert templates
    users = templates[-1]['users']
    assert len(users) == 1
    assert users[0] == user1
