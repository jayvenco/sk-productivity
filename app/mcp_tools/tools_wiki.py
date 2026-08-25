"""
MCP tools for the Wiki module.
"""
from app.database import SessionLocal
from app.models.wiki import WikiPage


def _page_to_json(page):
    return (
        f'{{"id":{page.id},"title":"{_escape(page.title)}","slug":"{_escape(page.slug)}",'
        f'"content":"{_escape(page.content)}",'
        f'"created_at":"{page.created_at.isoformat()}","updated_at":"{page.updated_at.isoformat()}"}}'
    )


def _pages_to_json(pages):
    items = ",".join(_page_to_json(p) for p in pages)
    return f'{{"items":[{items}],"total":{len(pages)}}}'


def _escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def register_wiki_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_wiki_list")
    def wiki_list() -> str:
        """List all wiki pages, ordered by most recent first."""
        db = SessionLocal()
        try:
            pages = db.query(WikiPage).order_by(WikiPage.created_at.desc()).all()
            return _pages_to_json(pages)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_wiki_get")
    def wiki_get(page_id: int) -> str:
        """Get a single wiki page by its ID."""
        db = SessionLocal()
        try:
            page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
            if not page:
                return '{"error": "Wiki page not found"}'
            return _page_to_json(page)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_wiki_get_by_slug")
    def wiki_get_by_slug(slug: str) -> str:
        """Get a wiki page by its URL slug."""
        db = SessionLocal()
        try:
            page = db.query(WikiPage).filter(WikiPage.slug == slug).first()
            if not page:
                return '{"error": "Wiki page not found"}'
            return _page_to_json(page)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_wiki_search")
    def wiki_search(query: str) -> str:
        """Search wiki pages by title or content."""
        db = SessionLocal()
        try:
            like = f"%{query}%"
            pages = db.query(WikiPage).filter(
                WikiPage.title.ilike(like) | WikiPage.content.ilike(like)
            ).order_by(WikiPage.created_at.desc()).all()
            return _pages_to_json(pages)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_wiki_create")
    def wiki_create(title: str, slug: str, content: str = "") -> str:
        """Create a new wiki page. Slug must be unique."""
        db = SessionLocal()
        try:
            existing = db.query(WikiPage).filter(WikiPage.slug == slug).first()
            if existing:
                return '{"error": "A page with this slug already exists"}'
            page = WikiPage(title=title, slug=slug, content=content)
            db.add(page)
            db.commit()
            db.refresh(page)
            return _page_to_json(page)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_wiki_edit")
    def wiki_edit(page_id: int, title: str = None, slug: str = None, content: str = None) -> str:
        """Edit an existing wiki page. Only provided fields are updated."""
        db = SessionLocal()
        try:
            page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
            if not page:
                return '{"error": "Wiki page not found"}'
            if title is not None:
                page.title = title
            if slug is not None:
                existing = db.query(WikiPage).filter(WikiPage.slug == slug, WikiPage.id != page_id).first()
                if existing:
                    return '{"error": "A page with this slug already exists"}'
                page.slug = slug
            if content is not None:
                page.content = content
            db.commit()
            db.refresh(page)
            return _page_to_json(page)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_wiki_delete")
    def wiki_delete(page_id: int) -> str:
        """Delete a wiki page by its ID."""
        db = SessionLocal()
        try:
            page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
            if not page:
                return '{"error": "Wiki page not found"}'
            db.delete(page)
            db.commit()
            return f'{{"deleted": true, "id": {page_id}}}'
        finally:
            db.close()