"""
Seed a demo account with example analyses.

Useful for looking at a populated dashboard without uploading photographs,
and for taking screenshots. The analyses are hand-written attribute sets run
through the real recommendation engine, so the advice shown is genuine — only
the detection step is skipped.

Usage:
    python seed_demo.py                       # demo@stylesense.ai / demo1234
    python seed_demo.py --email me@example.com --password hunter22
    python seed_demo.py --reset               # delete the account's analyses first
"""
import argparse
import sys

from app import create_app
from app.extensions import db
from app.models.analysis import Analysis
from app.models.feedback import Feedback
from app.models.user import User
from app.services.recommendation import generate_recommendations

DEFAULT_EMAIL = "demo@stylesense.ai"
DEFAULT_PASSWORD = "demo1234"

PROFILES = [
    {
        "face": {"shape": "oval", "confidence": 0.89},
        "skin": {"depth": "medium", "undertone": "warm", "hex_color": "#c68642",
                 "confidence": 0.81, "low_confidence_flag": False},
        "body": {"shape": "hourglass", "confidence": 0.84},
    },
    {
        "face": {"shape": "round", "confidence": 0.76},
        "skin": {"depth": "fair", "undertone": "cool", "hex_color": "#f0d5c0",
                 "confidence": 0.68, "low_confidence_flag": True},
        "body": {"shape": "pear", "confidence": 0.79},
    },
    {
        "face": {"shape": "square", "confidence": 0.83},
        "skin": {"depth": "deep", "undertone": "neutral", "hex_color": "#6b4423",
                 "confidence": 0.88, "low_confidence_flag": False},
        "body": {"shape": "rectangle", "confidence": 0.72},
    },
    {
        # Face-only: someone who uploaded a headshot and nothing else.
        "face": {"shape": "heart", "confidence": 0.80},
        "skin": {"depth": "tan", "undertone": "warm", "hex_color": "#a1683a",
                 "confidence": 0.75, "low_confidence_flag": False},
        "body": None,
    },
    {
        # Body-only: the other half of the same edge case.
        "face": None,
        "skin": None,
        "body": {"shape": "inverted_triangle", "confidence": 0.77},
    },
]


def seed(email: str, password: str, reset: bool) -> None:
    user = User.find_by_email(email)
    if user:
        print(f"Using existing account {email}")
    else:
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Created account {email}")

    if reset:
        removed = user.analyses.count()
        for analysis in user.analyses:
            db.session.delete(analysis)
        db.session.commit()
        print(f"Removed {removed} existing analyses")

    created = []
    for profile in PROFILES:
        face, skin, body = profile["face"], profile["skin"], profile["body"]

        analysis = Analysis(
            user_id=user.id,
            face_shape=face["shape"] if face else None,
            face_confidence=face["confidence"] if face else None,
            skin_depth=skin["depth"] if skin else None,
            skin_undertone=skin["undertone"] if skin else None,
            skin_hex_color=skin["hex_color"] if skin else None,
            skin_confidence=skin["confidence"] if skin else None,
            skin_low_confidence_flag=skin["low_confidence_flag"] if skin else False,
            body_shape=body["shape"] if body else None,
            body_confidence=body["confidence"] if body else None,
            recommendations=generate_recommendations(face, skin, body),
        )
        db.session.add(analysis)
        created.append(analysis)

    db.session.commit()

    # Like a couple of things so the Saved page is not empty either.
    liked = 0
    for analysis in created[:2]:
        for rec in (analysis.recommendations or [])[:2]:
            db.session.add(Feedback(
                user_id=user.id,
                analysis_id=analysis.id,
                category=rec["category"],
                recommendation=rec["recommendation"],
                verdict="like",
            ))
            liked += 1
    db.session.commit()

    print(f"Seeded {len(created)} analyses and {liked} saved recommendations")
    print(f"\nSign in with:  {email}  /  {password}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument(
        "--reset", action="store_true",
        help="delete the account's existing analyses before seeding",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if app.config.get("ENV") == "production":
            print(
                "Refusing to seed a production database. "
                "A demo account with a published password is not something "
                "you want reachable in production.",
                file=sys.stderr,
            )
            return 1
        seed(args.email, args.password, args.reset)

    return 0


if __name__ == "__main__":
    sys.exit(main())
