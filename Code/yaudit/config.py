"""Application Configuration."""
import os

LOCAL_DATABASE_URI_BASE = 'postgresql://localhost/Chemtrails'


class Config(object):
    """Parent configuration class."""

    TESTING = False
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')

    TITLE = "YAudit"
    VERSION = "0.1.0"
    DESCRIPTION = "Scripts for auditing YouTube."


class DevelopmentConfig(Config):
    """Configurations for Development."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default=LOCAL_DATABASE_URI_BASE)

    DEBUG = True


class TestingConfig(Config):
    """Configurations for Testing."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default=LOCAL_DATABASE_URI_BASE + '_testing')

    TESTING = True
    DEBUG = True


class StagingConfig(Config):
    """Configurations for Staging."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default=LOCAL_DATABASE_URI_BASE + '_staging')

    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default=LOCAL_DATABASE_URI_BASE + '_production')

    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}[os.getenv('APP_ENVIRONMENT', 'development')]()
