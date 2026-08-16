from neo4j import GraphDatabase
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def get_site_prefix(url: str | None):
    if not url:
        return None

    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        return None

    return f"{parsed.scheme}://{parsed.netloc}".lower()

def store_links(source_url, links):
    with driver.session(database="neo4j") as session:
        for link in links:
            session.run(
                """
                MERGE (source:Page {url: $source_url})
                MERGE (target:Page {url: $target_url})
                SET target.link_text = $link_text

                MERGE (source)-[:LINKS_TO]->(target)
                """,
                source_url=source_url,
                target_url=link["href"],
                link_text=link["text"]
            )
            
def store_page(url, title, text, content_hash):
    with driver.session(database="neo4j") as session:
        session.run(
            """
            MERGE (p:Page {url: $url})
            SET p.title = $title,
                p.text = $text,
                p.content_hash = $content_hash
            """,
            url=url,
            title=title,
            text=text,
            content_hash=content_hash
        )
        
        
def get_page(url):
    with driver.session(database="neo4j") as session:
        result = session.run(
            """
            MATCH (p:Page {url: $url})
            RETURN p.url AS url,
                   p.title AS title,
                   p.text AS text,
                   p.content_hash AS content_hash
            """,
            url=url
        )

        record = result.single()

        if record:
            return record.data()

        return None


def store_triplet(subject, relation, object_, source_url):
    with driver.session(database="neo4j") as session:
        session.run(
            """
            MERGE (s:Entity {name: $subject})
            MERGE (o:Entity {name: $object})

            MERGE (s)-[r:RELATED_TO {
                relation: $relation,
                source_url: $source_url
            }]->(o)
            """,
            subject=subject,
            relation=relation,
            object=object_,
            source_url=source_url
        )
        
def search_graph(search_text: str, current_url=None, limit: int = 10):
    import re

    stopwords = {
        "what", "when", "where", "who", "does", "say",
        "about", "the", "is", "are", "was", "were",
        "for", "to", "in", "on", "of"
    }

    words = [
        w for w in re.findall(r"[a-z0-9-]+", search_text.lower())
        if len(w) > 2 and w not in stopwords
    ]

    # If query contains several meaningful words,
    # require at least 2 of them to match.
    required_score = min(2, len(words))
    
    site_prefix = get_site_prefix(current_url)

    if not site_prefix:
        return []

    with driver.session(database="neo4j") as session:
        result = session.run(
            """
            MATCH (s:Entity)-[r:RELATED_TO]->(o:Entity)

            WHERE toLower(coalesce(r.source_url, "")) STARTS WITH $site_prefix

            WITH s, r, o,
                 [
                    word IN $words
                    WHERE toLower(s.name) CONTAINS word
                       OR toLower(o.name) CONTAINS word
                       OR toLower(r.relation) CONTAINS word
                 ] AS matches

            WHERE size(matches) >= $required_score

            RETURN s.name AS subject,
                   r.relation AS relation,
                   o.name AS object,
                   r.source_url AS source,
                   size(matches) AS score

            ORDER BY score DESC
            LIMIT $limit
            """,
            words=words,
            required_score=required_score,
            site_prefix=site_prefix,
            limit=limit
        )

        return [record.data() for record in result]

def search_pages(search_text: str, current_url=None, limit: int = 5):
    import re

    stopwords = {
        "what", "when", "where", "who", "does", "say",
        "about", "tell", "me", "the", "is", "are",
        "was", "were", "of", "to", "in", "on"
    }

    words = [
        w for w in re.findall(r"[a-z0-9-]+", search_text.lower())
        if len(w) > 2 and w not in stopwords
    ]
        
    site_prefix = get_site_prefix(current_url)

    if not site_prefix:
        return []

    with driver.session(database="neo4j") as session:
        result = session.run(
            """
            MATCH (p:Page)

            WHERE toLower(p.url) STARTS WITH $site_prefix

            WITH p,
                 [
                    word IN $words
                    WHERE toLower(coalesce(p.title, "")) CONTAINS word
                       OR toLower(coalesce(p.text, "")) CONTAINS word
                       OR toLower(p.url) CONTAINS word
                 ] AS matches

            WHERE size(matches) > 0

            RETURN p.url AS url,
                   p.title AS title,
                   p.text AS text,
                   size(matches) AS score

            ORDER BY score DESC
            LIMIT $limit
            """,
            words=words,
            site_prefix=site_prefix,
            limit=limit
        )

        return [record.data() for record in result]
    
def search_links(search_text: str, current_url=None, limit: int = 8):
    import re

    stopwords = {
        "what", "when", "where", "who", "does", "say",
        "about", "the", "is", "are", "to", "me", "open",
        "take", "go", "navigate", "current", "of"
    }

    words = [
        w for w in re.findall(r"[a-z0-9-]+", search_text.lower())
        if len(w) > 2 and w not in stopwords
    ]
        
    site_prefix = get_site_prefix(current_url)

    if not site_prefix:
        return []

    with driver.session(database="neo4j") as session:
        result = session.run(
            """
            MATCH (a:Page)-[:LINKS_TO]->(b:Page)

            WHERE toLower(a.url) STARTS WITH $site_prefix
            AND toLower(b.url) STARTS WITH $site_prefix

            WITH DISTINCT b,
                 [
                    word IN $words
                    WHERE toLower(coalesce(b.link_text, "")) CONTAINS word
                       OR toLower(coalesce(b.title, "")) CONTAINS word
                       OR toLower(b.url) CONTAINS word
                 ] AS matches

            WHERE size(matches) > 0

              AND NOT toLower(b.url) CONTAINS 'feedback'
              AND NOT toLower(b.url) CONTAINS 'captcha'
              AND NOT toLower(b.url) CONTAINS 'contact'
              AND NOT toLower(b.url) CONTAINS 'sitemap'

            RETURN b.url AS url,
                   b.title AS title,
                   b.link_text AS link_text,
                   size(matches) AS score

            ORDER BY score DESC
            LIMIT $limit
            """,
            words=words,
            site_prefix=site_prefix,
            limit=limit
        )

        return [record.data() for record in result]