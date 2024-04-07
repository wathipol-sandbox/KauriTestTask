from fastapi import APIRouter, Depends
from app.dependencies import get_auth_api_token, validate_ws_auth_api_token
from typing import Optional


def make_base_router(
		tags,
		basic_auth: Optional[bool] = True, ws_auth: Optional[bool] = False, **kwargs):
	"""Make FastAPI router object with basic API settings.
            IF basic_auth is True the endpoint will be protected by default authorization depeend method.
                All kwargs wiil be passed to APIRouter constructor
    """
    
	base_kwargs = {
		"tags": [tags] if isinstance(tags,str) else tags,
		"dependencies":[dp for dp in kwargs.get("dependencies", [])]
	}
	if basic_auth is True:
		base_kwargs["dependencies"].append(get_auth_api_token)
	if ws_auth is True:
		base_kwargs["dependencies"].append(validate_ws_auth_api_token)
	if "dependencies" in kwargs:
		del kwargs["dependencies"]
	base_kwargs.update(kwargs)
	base_kwargs["dependencies"] = [Depends(d) for d in base_kwargs["dependencies"]]
	return APIRouter(**base_kwargs)
