# tests myWall functionality
from monolith.database import Story


def test_check_mywall(client, auth, database, templates):
    reply = client.get('/')
    assert reply.status_code == 302

    auth.login()

    reply = client.get('/')
    stories = templates[-1]['stories']
    assert reply.status_code == 200
    assert stories == []

    example = Story()
    # gets story_id=1 as user_id or as the first?
    example.text = 'Trial story of example admin user :)'
    example.likes = 42
    example.dislikes = 0
    example.author_id = 1
    example.dice_set = 'face1?face2?face3?face4'
    database.session.add(example)
    database.session.commit()

    reply = client.get('/')
    stories = templates[-1]['stories']
    assert reply.status_code == 200
    assert len(stories) == 1
    assert stories[0].id == example.id

    example2 = Story()
    # gets story_id=1 as user_id or as the first?
    example2.text = 'New story of example admin user :)'
    example2.likes = 42
    example2.dislikes = 0
    example2.author_id = 1
    example2.dice_set = 'face1?face2?face3?face4'
    database.session.add(example2)
    database.session.commit()

    reply = client.get('/')
    stories = templates[-1]['stories']

    assert reply.status_code == 200
    assert len(stories) == 2
    for story in stories:
        assert story.id == example.id or story.id == example2.id


def test_statistics(client, auth, database, templates):
    auth.login()

    reply = client.get('/')

    assert reply.status_code == 200
    # As soon as I create a new user I shouldn't have stats
    # since I have no stories
    stats = templates[-1]['stats']
    assert stats == {}

    example = Story()
    example.text = 'Lorem ipsum dolor sit amet'
    example.likes = 0
    example.dislikes = 0
    example.author_id = 1
    example.dice_set = ["face1", "face2", "face3", "face4"]
    database.session.add(example)
    database.session.commit()

    reply = client.get('/')
    stats = templates[-1]['stats']
    assert reply.status_code == 200
    # List index 0 refers to number of stories,
    # index 1 refers to the number of likes,
    # index 2 to the number of dislikes
    assert stats['stories'][0] == 1 \
        and stats['stories'][1] == 0 \
        and stats['stories'][2] == 0

    # I threw one set of four dice only once
    assert stats['avg_dice'] == 4

    # Published only only one story
    assert stats['stories_frequency'] == 1

    # Active user, it has been published at least one story in the last 7 days
    assert stats['active']
