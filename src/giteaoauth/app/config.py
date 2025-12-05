"""Configuration for the Gitea OAuth application."""

from giteaoauth.models.app_config import AppConfig

config = AppConfig.from_jsonfile("config.json")
