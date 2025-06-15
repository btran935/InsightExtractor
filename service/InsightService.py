
import requests
import json
import feedparser
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import Session, select, func
from database import engine
from sentence_transformers import SentenceTransformer
from models.models import Theme, Post
from datetime import datetime, timezone

model = SentenceTransformer("all-MiniLM-L6-v2")
SIM_THRESHOLD = 0.8



def ingest_feed_url(feed_url: str)  :

    """
       ingest feed, parse, find existing matching themes if available, then write to posts/themes table accordingly
    """

    ## extract RSS feed
    ## post to tables using sql
    ## extract posts
    ## extract themes
    feed = feedparser.parse(feed_url)
    with Session(engine) as session:
        for entry in feed.entries:
            link = entry.get("link")
            ## run sql query to ensure duplicate not inserted if feed is re-ingested
            if session.exec(select(Post).where(Post.post_url == link)).first():
                continue

            ## grab thesis
            thesis = entry.get('summary') or entry.get('title')
            ## outputs a numeric vector representing the sentence semantically
            embed_vec = model.encode([thesis])[0]
            ## loop to find an existing theme that matches semantically and assign theme to that
            theme = None
            for t in session.exec(select(Theme)).all():
                existing_vec = json.loads(t.embedding or "[]")
                similarity = cosine_similarity([embed_vec], [existing_vec])[0][0]
                if similarity >= SIM_THRESHOLD:
                    theme = t
                    break

            ## if no matching theme found, write new theme to table
            if not theme:
                theme = Theme(thesis_text=thesis, embedding=json.dumps(list(embed_vec.tolist())))
                session.add(theme)
                session.commit()
            published = entry.get("published_parsed")
            if published:
                published_at = datetime(*published[:6], tzinfo=timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)

            ## write post to db
            post = Post(
                theme_id=theme.id,
                post_title=entry.get("title"),
                post_url=link,
                published_at=published_at,
                thesis_text=thesis
            )
            session.add(post)
            session.commit()

def get_all_themes() -> list[dict]:
    """
       list all themes with the count of posts supporting each
    """
    with Session(engine) as session:
        statement = (
            select(
                Theme.id,
                Theme.thesis_text,
                func.count(Post.id).label("post_count")
            )
            .join(Post, Theme.id == Post.theme_id)
            .group_by(Theme.id)
        )
        results = session.exec(statement).all()

        # Format results for JSON response
    return [
        {"id": theme_id, "thesis_text": thesis, "post_count": post_count}
        for theme_id, thesis, post_count in results
    ]

def get_theme_by_id(theme_id: int):
    """
       Return the specified theme and its posts in chronological order.
       If the theme does not exist, return None.
    """
    with Session(engine) as session:
        theme = session.get(Theme, theme_id)
        if not theme:
            return None
        statement = (
            select(Post)
            .where(Post.theme_id == theme_id)
            .order_by(Post.published_at)  # chronological order
        )
        posts = session.exec(statement).all()
    return {
        "id": theme.id,
        "thesis_text": theme.thesis_text,
        "posts": [
            {
                "id": post.id,
                "title": post.post_title,
                "url": post.post_url,
                "published_at": post.published_at.isoformat(),
                "thesis_text": post.thesis_text,
            }
            for post in posts
        ],
    }