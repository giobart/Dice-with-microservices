from monolith.database import Story


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


def test_delete_story(client, auth, database, templates):
    auth.login()

    reply = client.delete('/stories/0') # delete non-existing story
    assert reply.status_code == 404

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

    auth.logout()

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

    auth.login()

    # delete story of another user
    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 403
