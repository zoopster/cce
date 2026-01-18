"""
Publishing endpoints.

Handles content export and publishing to various platforms.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..agents.publisher import PublisherAgent
from ..models.content import ContentSession, SessionStatus, ContentVersion
from ..tools.memory import read_from_memory, list_memory_keys
from .sessions import sessions

router = APIRouter(prefix="/api/sessions", tags=["publish"])


def sync_versions_from_memory(session: ContentSession) -> None:
    """
    Sync session.versions from filesystem memory.

    This fixes the issue where content is saved to filesystem
    but not reflected in the in-memory session object.
    """
    if session.versions:
        return  # Already has versions

    # Find version files in memory
    version_keys = list_memory_keys(session.session_id, prefix="versions/")

    for key in sorted(version_keys):
        version_data = read_from_memory(session.session_id, key)
        if version_data:
            version = ContentVersion(
                version_number=version_data.get("version_number", 1),
                content=version_data.get("content", ""),
                generated_at=datetime.fromisoformat(version_data.get("generated_at", datetime.utcnow().isoformat())),
                feedback_applied=version_data.get("feedback_applied")
            )
            session.versions.append(version)


class WordPressPublishRequest(BaseModel):
    """Request body for WordPress publishing."""
    site_url: str
    username: str
    app_password: str
    status: str = "draft"  # draft or publish
    categories: Optional[List[int]] = None
    tags: Optional[List[int]] = None


@router.post("/{session_id}/publish/wordpress")
async def publish_to_wordpress(session_id: str, request: WordPressPublishRequest):
    """
    Publish content to WordPress via REST API.

    Requires WordPress site with REST API enabled and application password.

    Args:
    - site_url: WordPress site URL (e.g., https://example.com)
    - username: WordPress username
    - app_password: WordPress application password (not regular password)
    - status: 'draft' or 'publish'
    - categories: Optional list of category IDs
    - tags: Optional list of tag IDs

    Returns:
    - post_id: WordPress post ID
    - url: Public URL of the post
    - edit_url: WordPress admin edit URL
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sync_versions_from_memory(session)

    if not session.versions:
        raise HTTPException(status_code=400, detail="No content to publish")

    publisher = PublisherAgent(session)

    try:
        result = await publisher.publish_to_wordpress(
            site_url=request.site_url,
            username=request.username,
            app_password=request.app_password,
            status=request.status,
            categories=request.categories,
            tags=request.tags
        )

        session.status = SessionStatus.PUBLISHED

        return {
            "status": "success",
            "post_id": result["post_id"],
            "url": result["url"],
            "edit_url": result["edit_url"],
            "published_status": result["status"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Publishing failed: {str(e)}"
        )


@router.post("/{session_id}/publish/html")
async def export_to_html(session_id: str):
    """
    Export content as HTML with embedded styles.

    Returns HTML content, filename, and metadata.
    Does not write to filesystem - client receives HTML for download.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sync_versions_from_memory(session)

    if not session.versions:
        raise HTTPException(status_code=400, detail="No content to export")

    publisher = PublisherAgent(session)
    result = publisher.export_to_html(include_styles=True)

    return {
        "status": "success",
        "filename": result["filename"],
        "title": result["title"],
        "html": result["html"],
        "exported_at": result["exported_at"]
    }


@router.get("/{session_id}/preview")
async def preview_html(session_id: str):
    """
    Preview content as rendered HTML.

    Returns fully styled HTML page for browser preview.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sync_versions_from_memory(session)

    if not session.versions:
        raise HTTPException(status_code=400, detail="No content to preview")

    publisher = PublisherAgent(session)
    result = publisher.export_to_html(include_styles=True)

    return HTMLResponse(content=result["html"])


@router.get("/{session_id}/download")
async def download_html(session_id: str):
    """
    Download content as HTML file.

    Returns HTML file with Content-Disposition header for browser download.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sync_versions_from_memory(session)

    if not session.versions:
        raise HTTPException(status_code=400, detail="No content to download")

    publisher = PublisherAgent(session)
    result = publisher.export_to_html(include_styles=True)

    return Response(
        content=result["html"],
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{result["filename"]}"'
        }
    )


@router.post("/{session_id}/verify-citations")
async def verify_citations(session_id: str):
    """
    Verify all citations/links in the content.

    Checks each URL to ensure it's valid and accessible.

    Returns:
    - total_links: Total number of links found
    - valid_count: Number of valid links
    - invalid_count: Number of broken/invalid links
    - invalid_links: List of broken links with details
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sync_versions_from_memory(session)

    if not session.versions:
        raise HTTPException(status_code=400, detail="No content to verify")

    publisher = PublisherAgent(session)

    try:
        result = await publisher.verify_citations()

        return {
            "status": "complete",
            "total_links": result["total_links"],
            "valid_count": len(result["valid"]),
            "invalid_count": len(result["invalid"]),
            "valid_links": result["valid"],
            "invalid_links": result["invalid"],
            "checked_at": result["checked_at"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Citation verification failed: {str(e)}"
        )


@router.get("/{session_id}/markdown")
async def get_markdown(session_id: str):
    """
    Get the raw markdown content.

    Returns the current content version in markdown format.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sync_versions_from_memory(session)

    if not session.versions:
        raise HTTPException(status_code=404, detail="No content available")

    latest = session.versions[-1]

    return Response(
        content=latest.content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{session.topic.lower().replace(" ", "-")}.md"'
        }
    )
