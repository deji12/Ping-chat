import json
import os
import sys
from django.conf import settings

cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(cur_path)[0]
sys.path.append(root_path)
from .token04.src import token04

def generate_token(user_id, room_id):

    app_id = settings.ZEGO_APP_ID
    server_secret = settings.ZEGO_SERVER_SECRET

    # Token expiration time, unit: seconds
    effective_time_in_seconds = 3600

    # The permission control information of the permission authentication token is controlled by the payload
    payload = {
        "room_id": room_id, # Room ID
        "privilege": {
            1 : 1, # key 1 represents room permission, value 1 represents allowed, so here means allowing room login; if the value is 0, it means not allowed
            2 : 1  # key 2 represents push permission, value 1 represents allowed, so here means allowing push; if the value is 0, it means not allowed
        }, 
        "stream_id_list": None # Passing None means that all streams can be pushed. If a streamID list is passed in, only the streamIDs in the list can be pushed
    }

    # 3600 is the token expiration time, unit: seconds
    token_info = token04.generate_token04(
        app_id=app_id, 
        user_id=user_id, 
        secret=server_secret,
        effective_time_in_seconds=effective_time_in_seconds, 
        payload=json.dumps(payload)
    )
    # print([token_info.token, token_info.error_code, token_info.error_message])

    return token_info.token