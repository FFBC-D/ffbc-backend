from fastapi import HTTPException, status


def get_token_from_bearer_string(bearer_string: str) -> str:
    try:
        return bearer_string.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Bearer string",
        )
