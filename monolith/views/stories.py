from flask import Blueprint, redirect, render_template, request, abort
from monolith.database import db, Story, Like
from monolith.auth import admin_required, current_user
from flask_login import (current_user, login_user, logout_user, login_required)
from monolith.utility.diceutils import *
from monolith.forms import *
from monolith.classes.DiceSet import *

stories = Blueprint('stories', __name__)


@stories.route('/newStory', methods=['GET', 'POST'])
@login_required
def _newstory():
    form = StoryForm()
    if request.method == 'POST':
        diceset = request.form['diceset']
        if form.validate_on_submit():
            # new story inserted #
            # TODO: write a story on the rolled dice #
            return render_template("stories.html")

    if request.method == 'GET':
        return render_template("new_story.html", diceset=get_dice_sets_lsit())


@stories.route('/rollDice', methods=['GET'])
@login_required
def _rollDice():
    form = StoryForm()
    diceset = request.args.get('diceset')
    # default choose standard diceset
    if diceset is None:
        diceset = 'standard'

    try:
        dice = DiceSet(diceset, 6)
        roll = dice.throw_dice()
    except Exception as e:
        abort(404)

    return render_template("new_story.html", dice=roll, form=form)


@stories.route('/stories')
def _stories(message=''):
    allstories = db.session.query(Story)
    return render_template("stories.html", message=message, stories=allstories,
                           like_it_url="http://127.0.0.1:5000/stories/like/")


@stories.route('/stories/like/<authorid>/<storyid>')
@login_required
def _like(authorid, storyid):
    q = Like.query.filter_by(liker_id=current_user.id, story_id=storyid)
    if q.first() != None:
        new_like = Like()
        new_like.liker_id = current_user.id
        new_like.story_id = storyid
        new_like.liked_id = authorid
        db.session.add(new_like)
        db.session.commit()
        message = ''
    else:
        message = 'You\'ve already liked this story!'
    return _stories(message)
