import pytest
from webproject.routes.requests import group_requests,check_guests

def test_check_guests():
    players = [2,4,1,6,7]
    guests = [7]
    groups = group_requests(players,guests)
    assert len([group for group in groups if len(group) > 4]) == 0