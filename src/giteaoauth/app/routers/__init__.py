"""Routers for the Gitea OAuth application."""

from giteaoauth.app.routers.auth import router as auth_router

routers = [auth_router]

__all__ = ["routers"]
