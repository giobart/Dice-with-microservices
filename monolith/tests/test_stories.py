from monolith.database import Story
from sqlalchemy import desc
import datetime as dt
import pytest

def test_new_story_selection(client, auth):
    auth.login()
    # new story page
    reply = client.get('/new_story')
    assert reply.status_code == 200


def test_new_story(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']
    story = database.session.query(Story).get(new_id)
    assert story.text == ''
    assert story.author_id == 1
    assert story.is_draft
    assert story.likes == 0
    assert story.dislikes == 0


def test_edit_story(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    story = database.session.query(Story).order_by(Story.date.desc()).first()
    assert story.text == story_text
    assert story.author_id == 1

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']
    reply = client.post(f'/stories/{new_id}/edit', data={})
    assert reply.status_code == 200
    form = templates[-1]['form']
    assert 'This field is required.' in form.text.errors


def test_edit_non_draft_story(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']
    roll = templates[-1]['dice']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit',
                        data={'text': story_text})
    assert reply.status_code == 302
    story = database.session.query(Story).get(new_id)
    assert not story.is_draft

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 403


def test_edit_not_author_story(client, auth, database, templates):
    auth.login()
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']
    auth.logout()

    auth.login('test1', 'test1123')
    reply = client.post(f'/stories/{new_id}/edit',
                        data={'text': ''})
    assert reply.status_code == 401


def test_edit_non_existent_story(client, auth, database):
    auth.login()
    reply = client.get('/stories/0/edit')
    assert reply.status_code == 404


def test_edit_deleted_story(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']

    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 200

    reply = client.get(f'/stories/{new_id}/edit')
    assert reply.status_code == 410


def test_edit_not_valid_story(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story = ''
    for i in range(1, len(roll)):
        story = story + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit',
                        data={'text': story})
    database.session.commit()
    assert reply.status_code == 200
    form = templates[-1]['form']
    assert 'The story is not valid.' in form.text.errors


def test_edit_draft_valid_story(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']

    reply = client.post(f'/stories/{new_id}/edit',
                        data={'text': 'blob', 'is_draft': 'y'})
    database.session.commit()
    assert reply.status_code == 302


def test_edit_get(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.get(f'/stories/{new_id}/edit')
    assert reply.status_code == 200
    template_capture = templates[-1]
    assert template_capture['story_id'] == new_id
    assert template_capture['dice'] == roll

def test_empty_story_list(client, auth, database, templates):
    reply = client.get('/stories')
    assert reply.status_code == 200
    stories = templates[-1]['stories']
    assert stories.count() == 0 # no loaded stories

def test_nonempty_story_list(client, auth, database, templates):
    auth.login()

    # add 1 story
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    #check only 1 story is present
    reply = client.get('/stories')
    assert reply.status_code == 200
    stories = templates[-1]['stories']
    assert stories.count() == 1
    #and it is the one just published
    query = database.session.query(Story).filter_by(deleted=False).order_by(desc(Story.date))
    assert query.count() == stories.count()
    assert query[0].id == stories[0].id
    assert query[0].text == stories[0].text
    assert query[0].author_id == stories[0].author_id

    #add another story
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    #check all stories are present
    reply = client.get('/stories')
    assert reply.status_code == 200
    stories = templates[-1]['stories']
    assert stories.count() == 2

    #check that queried and rendered items are the same
    query = database.session.query(Story).filter_by(deleted=False).order_by(desc(Story.date))

    assert stories.count() == query.count()

    for i in range(stories.count()):
        assert query[i].id == stories[i].id
        assert query[i].text == stories[i].text

def test_delete_nonexisting_story(client, auth, database, templates):
    auth.login()

    reply = client.delete('/stories/0')  # delete non-existing story
    assert reply.status_code == 404

def test_delete_existing_story(client, auth, database, templates):
    auth.login()

    # new story
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    # delete the newly created story
    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 200
    deletedStory = database.session.query(Story).get(new_id)
    assert deletedStory.deleted

def test_delete_already_deleted_story(client, auth, database, templates):
    auth.login()

    # new story
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    # delete the newly created story
    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 200
    deletedStory = database.session.query(Story).get(new_id)
    assert deletedStory.deleted

    # delete already deleted story
    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 400

    # delete already deleted story again
    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 400

def test_delete_story_of_another_user(client, auth, database, templates):
    auth.login('test1', 'test1123')
    # new story by user test1
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302
    auth.logout()

    auth.login('test2', 'test2123')

    # delete story of another user
    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 403

@pytest.fixture
def init_database(database):
    example = Story()
    example.text = 'lorem ipsum dolor sit amet'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2018, month=12, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'bird drink coffee baloon'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=1, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'lorem Coffee dolor sit amet'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=3, day=12)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'bird cofFee baloon amet'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2017, month=10, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    database.session.commit()


def test_all_stories(client, templates, init_database):
    reply = client.get('/stories')
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    message = templates[-1]['message']
    assert stories.count() == 4
    assert message == ''


def test_query_story(client, templates, init_database):
    # valid query params, no matches
    reply = client.get('/stories?q=foo')
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    assert not stories.all()

    # valid query params, single word
    reply = client.get('/stories?q=dolor')
    assert reply.status_code == 200
    stories = templates[-1]['stories'].all()
    assert len(stories) == 2
    for s in stories:
        assert 'dolor' in s.text

    # valid query params, multiple word
    reply = client.get('/stories?q=lorem dolor')
    assert reply.status_code == 200
    stories = templates[-1]['stories'].all()
    assert len(stories) == 2
    for s in stories:
        assert 'lorem' in s.text or 'dolor' in s.text

    # valid query params, case insensitive
    reply = client.get('/stories?q=CoFFeE')
    assert reply.status_code == 200
    stories = templates[-1]['stories'].all()
    assert len(stories) == 3
    for s in stories:
        assert 'coffee' in s.text.lower()
