"""Gitea OAuth2 Authentication Router."""

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse

from giteaoauth.app.config import config

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="gitea",
    client_id=config.client_id,
    client_secret=config.client_secret,
    server_metadata_url=f"{config.gitea_internal_url}/.well-known/openid-configuration",
    access_token_url=f"{config.gitea_internal_url}/login/oauth/access_token",
    authorize_url=f"{config.gitea_public_url}/login/oauth/authorize",
    client_kwargs={
        "scope": "openid profile email",
        "code_challenge_method": "S256",
        "verify": False,
    },
)


@router.get("/login")
async def login(request: Request):
    """Gitea OAuth2 Login Endpoint."""
    print("login")
    redirect_uri = request.url_for("auth_callback")
    print("auth callback")
    print(redirect_uri)
    return await oauth.gitea.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request):
    """Gitea OAuth2 Callback Endpoint."""
    token = await oauth.gitea.authorize_access_token(request)
    claims = token.get("userinfo")
    if not claims:
        claims = await oauth.gitea.userinfo(token=token)
    request.session["user"] = {
        "sub": claims.get("sub"),
        "name": claims.get("name"),
        "email": claims.get("email"),
        "preferred_username": claims.get("preferred_username"),
    }
    return RedirectResponse(url="/fastapi/auth/me")


@router.get("/me")
async def me(request: Request):
    """Get authenticated user information."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="not authenticated")
    return JSONResponse(user)


@router.get("/")
def root():
    """Root endpoint to check if the service is running."""
    return {"ok": True}
