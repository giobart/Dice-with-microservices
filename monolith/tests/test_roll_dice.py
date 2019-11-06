from monolith.utility.diceutils import get_die_faces_list


def test_roll_valid_dice_success(client, auth):
    auth.login()
    reply = client.get('/roll_dice?diceset=standard')
    assert reply.status_code == 302


def test_roll_invalid_dice_fail(client, auth):
    auth.login()
    # new story page
    reply = client.get('/roll_dice?diceset=LukeImYourFather')
    assert reply.status_code == 400

    # 3 standard dice
    reply = client.get('/roll_dice?diceset=standard&dicenum=3')
    assert reply.status_code == 400

    # -1 standard dice
    reply = client.get('/roll_dice?diceset=standard&dicenum=-1')
    assert reply.status_code == 400

    # 0 standard dice
    reply = client.get('/roll_dice?diceset=standard&dicenum=0')
    assert reply.status_code == 400


def test_roll_dice_standard(client, auth, templates):
    auth.login()
    # 6 standard dice
    reply = client.get('/roll_dice?diceset=standard', follow_redirects=True)
    assert reply.status_code == 200
    template_capture = templates[-1]['dice']
    assert len(template_capture) == 6

    # 5 standard dice
    reply = client.get('/roll_dice?diceset=standard&dicenum=5',
                       follow_redirects=True)
    assert reply.status_code == 200
    template_capture = templates[-1]['dice']
    assert len(template_capture) == 5

    # 4 standard dice
    reply = client.get('/roll_dice?diceset=standard&dicenum=4',
                       follow_redirects=True)
    assert reply.status_code == 200
    template_capture = templates[-1]['dice']
    assert len(template_capture) == 4


def test_roll_dice_halloween(client, auth, templates):
    auth.login()
    # dice thrown in halloween set
    reply = client.get('/roll_dice?diceset=halloween', follow_redirects=True)
    assert reply.status_code == 200
    template_capture = templates[-1]['dice']
    assert len(template_capture) == 6
    for i in range(0, 6):
        face_list = get_die_faces_list('halloween', i)
        assert template_capture[i] in face_list


def test_roll_dice_xmas(client, auth, templates):
    auth.login()
    # dice thrown in xmas set
    reply = client.get('/roll_dice?diceset=xmas', follow_redirects=True)
    assert reply.status_code == 200
    template_capture = templates[-1]['dice']
    assert len(template_capture) == 6
    for i in range(0, 6):
        face_list = get_die_faces_list('xmas', i)
        assert template_capture[i] in face_list
