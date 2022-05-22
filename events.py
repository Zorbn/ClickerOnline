import time
import eventlet

from producers import (PRODUCER_STATS, default_producers_to_text,
                       producers_to_text, text_to_producers)

from flask import request
from flask_socketio import SocketIO

from flask_login import current_user
from flask_socketio import emit

from models import Stats, db
from app import MAX_MONEY


eventlet.monkey_patch()
socketio = SocketIO(async_mode="eventlet")

current_sids = []


def change_money(user_stats, change):
    """
    Utility function to make sure money obeys game rules and
    doesn't overflow. Returns that actual change in money.
    """

    prev_money = user_stats.money
    user_stats.money += change

    if (user_stats.money > MAX_MONEY):
        user_stats.money = MAX_MONEY
        return MAX_MONEY - prev_money

    if (user_stats.money < 0):
        user_stats.money = 0
        return prev_money

    return change


def game_loop(sid, uid):
    last_payouts = {}

    for producer in PRODUCER_STATS:
        last_payouts[producer] = time.time()

    while True:
        session = db.create_scoped_session()
        current_time = time.time()
        user_stats = session.get(Stats, uid)
        profit = 0

        user_producers = text_to_producers(user_stats.producers)

        for producer in last_payouts:
            stats = PRODUCER_STATS[producer]
            if last_payouts[producer] + stats["delay"] <= current_time:
                profit += stats["value"] * user_producers[producer]
                last_payouts[producer] = current_time

        if profit != 0:
            received = change_money(user_stats, profit)
            session.commit()

            socketio.emit("receive_money", received, room=sid)

        session.remove()

        if sid not in current_sids:
            return

        eventlet.sleep()  # Release CPU to the rest of the program to run.


@socketio.on("connect")
def connect():
    current_sids.append(request.sid)
    socketio.start_background_task(
        game_loop, request.sid, current_user.get_id())


@socketio.on("disconnect")
def disconnect():
    current_sids.remove(request.sid)


@socketio.event
def request_money():
    if not current_user.is_authenticated:
        return

    user_id = current_user.get_id()
    user_stats = db.session.get(Stats, user_id)
    received = change_money(user_stats, 20)
    db.session.commit()

    emit("receive_money", received)


@socketio.event
def request_total_money():
    if not current_user.is_authenticated:
        return

    user_id = current_user.get_id()
    user_stats = db.session.get(Stats, user_id)

    emit("receive_total_money", user_stats.money)


@socketio.event
def request_total_producers():
    if not current_user.is_authenticated:
        return

    user_id = current_user.get_id()
    user_stats = db.session.get(Stats, user_id)
    user_producers = text_to_producers(user_stats.producers)

    emit("receive_total_producers", user_producers)


@socketio.event
def request_producer_stats():
    if not current_user.is_authenticated:
        return

    emit("receive_producer_stats", PRODUCER_STATS)


@socketio.event
def request_total_prestiges():
    if not current_user.is_authenticated:
        return

    user_id = current_user.get_id()
    user_stats = db.session.get(Stats, user_id)

    emit("receive_total_prestiges", user_stats.prestiges)


@socketio.event
def request_buy_producer(type):
    if not current_user.is_authenticated:
        return

    user_id = current_user.get_id()
    user_stats = db.session.get(Stats, user_id)
    user_producers = text_to_producers(user_stats.producers)

    if type not in user_producers:
        return

    if user_stats.money < PRODUCER_STATS[type]["cost"]:
        return

    spent = change_money(user_stats, -PRODUCER_STATS[type]["cost"])
    user_producers[type] += 1
    user_stats.producers = producers_to_text(user_producers)
    db.session.commit()

    emit("receive_buy_producer", (type, user_producers[type]))
    emit("receive_spent_money", -spent)


@socketio.event
def request_prestige():
    if not current_user.is_authenticated:
        return

    user_id = current_user.get_id()
    user_stats = db.session.get(Stats, user_id)

    if user_stats.money >= MAX_MONEY:
        user_stats.prestiges += 1
        user_stats.money = 0
        user_stats.producers = default_producers_to_text()
        db.session.commit()

        user_producers = text_to_producers(user_stats.producers)

        emit("receive_total_money", user_stats.money)
        emit("receive_total_producers", user_producers)
        emit("receive_total_prestiges", user_stats.prestiges)
