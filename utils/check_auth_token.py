

from typing import Optional
from fastapi import HTTPException

from utils.database.remote_smart_home_database import RemoteSmartHomeDatabase
from utils.header_decoder import header_decoder


def verify_auth_token(database_handler: RemoteSmartHomeDatabase, authorization: Optional[str]) -> str:
    try:
        auth_token = header_decoder(authorization)
        user_result = database_handler.user_session.get_session(
            {"token": auth_token}
        )
        if len(user_result) != 1:
            raise ValueError()
    except ValueError:
        raise HTTPException(401, {
            "message":  "Unauthorized access.",
        })
    # Return out the userId fom the user object.
    return user_result[0]["userId"]
