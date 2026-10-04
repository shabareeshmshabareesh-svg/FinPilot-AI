import os

from datetime import timedelta

from dotenv import load_dotenv


# =========================================
# LOAD ENVIRONMENT VARIABLES
# =========================================

load_dotenv()


# =========================================
# BASE DIRECTORY
# =========================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


# =========================================
# ENVIRONMENT HELPERS
# =========================================

def _env_bool(name, default=False):

    raw = os.environ.get(name, "").strip().lower()

    if not raw:

        return default

    return raw in {"1", "true", "yes", "on"}


# =========================================
# APPLICATION CONFIGURATION
# =========================================

class Config:

    # -------------------------------------
    # SECRET KEY
    # -------------------------------------

    SECRET_KEY = os.environ.get(
        "FINPILOT_SECRET_KEY"
    )

    if not SECRET_KEY:
        raise RuntimeError(
            "FINPILOT_SECRET_KEY is not set"
        )


    # -------------------------------------
    # DATABASE
    # -------------------------------------
    #
    # FINPILOT_DATABASE_URI is optional.
    # It is only used for automated checks or
    # deployments that need a different file.
    # The default stays the local SQLite file,
    # so normal use is unchanged.

    SQLALCHEMY_DATABASE_URI = (

        os.environ.get(
            "FINPILOT_DATABASE_URI"
        )

        or

        (
            "sqlite:///"
            + os.path.join(
                BASE_DIR,
                "instance",
                "finpilot.db"
            )
        )

    )


    # -------------------------------------
    # SQLALCHEMY
    # -------------------------------------

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # -------------------------------------
    # SESSION SECURITY
    # -------------------------------------
    #
    # The session cookie is HTTP only and is not
    # attached to cross site requests.
    #
    # SESSION_COOKIE_SECURE stays off by default
    # so local development over http works.
    # Enable it for HTTPS deployments with:
    #
    #     FINPILOT_COOKIE_SECURE=1

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (

        os.environ.get(
            "FINPILOT_COOKIE_SECURE",
            ""
        ).strip().lower()

        in {"1", "true", "yes", "on"}

    )

    PERMANENT_SESSION_LIFETIME = timedelta(
        days=7
    )


    # -------------------------------------
    # REQUEST SIZE LIMIT
    # -------------------------------------
    #
    # FinPilot only submits small forms, so a
    # 2 MB ceiling is generous and protects the
    # app from oversized request bodies.

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024