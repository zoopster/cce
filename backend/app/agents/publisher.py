"""
Publisher Agent - Handles content publishing to WordPress and HTML export.

Key responsibilities:
1. Format content for target platform
2. Publish to WordPress via REST API
3. Export as standalone HTML
4. Verify citations and links
"""

import httpx
import markdown
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .base import BaseAgent
from ..tools.memory import read_from_memory, save_to_memory
from ..models.content import ContentSession, AgentState
from ..config import settings


class PublisherAgent(BaseAgent):
    """
    Handles publishing content to various targets.

    Supports:
    - WordPress REST API publishing
    - Standalone HTML export
    - Citation verification
    """

    def __init__(self, session: ContentSession):
        super().__init__(session.session_id, agent_id="publisher")
        self.session = session
        self.current_task = "initializing"

    def _get_current_content(self) -> str:
        """Get the most recent content version."""
        if self.session.versions:
            return self.session.versions[-1].content

        for i in range(10, 0, -1):
            version_data = read_from_memory(self.session_id, f"versions/v{i}")
            if version_data:
                return version_data.get("content", "")

        return ""

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content (first H1)."""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return self.session.topic

    def _markdown_to_html(self, content: str) -> str:
        """Convert markdown to HTML."""
        return markdown.markdown(
            content,
            extensions=['fenced_code', 'tables', 'toc', 'nl2br']
        )

    async def _check_mcp_support(self, site_url: str) -> bool:
        """Check if WordPress site supports MCP protocol."""
        mcp_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/wpmcp/streamable"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(mcp_url, timeout=5.0)
                # MCP endpoint exists if we get any response (even 401 unauthorized)
                return response.status_code in [200, 401, 405]
        except:
            return False

    async def _publish_via_mcp(
        self,
        site_url: str,
        username: str,
        app_password: str,
        title: str,
        html_content: str,
        status: str
    ) -> Dict[str, Any]:
        """Publish via WordPress MCP protocol."""
        import base64

        mcp_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/wpmcp/streamable"

        # Create Basic Auth token
        credentials = f"{username}:{app_password}"
        auth_token = base64.b64encode(credentials.encode()).decode()

        # MCP JSON-RPC request to create post
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "create_post",
                "arguments": {
                    "title": title,
                    "content": html_content,
                    "status": status
                }
            },
            "id": 1
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                mcp_url,
                json=mcp_request,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {auth_token}"
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise Exception(result["error"].get("message", "MCP error"))

            # Extract post data from MCP response
            post_data = result.get("result", {})
            return {
                "post_id": post_data.get("id"),
                "url": post_data.get("link"),
                "edit_url": f"{site_url}/wp-admin/post.php?post={post_data.get('id')}&action=edit",
                "status": post_data.get("status", status),
                "method": "mcp"
            }

    async def publish_to_wordpress(
        self,
        site_url: str,
        username: str,
        app_password: str,
        status: str = "draft",
        categories: List[int] = None,
        tags: List[int] = None
    ) -> Dict[str, Any]:
        """
        Publish content to WordPress via MCP or REST API.

        Tries MCP protocol first if the site supports it, then falls back to REST API.

        Args:
            site_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            app_password: WordPress application password
            status: 'draft' or 'publish'
            categories: List of category IDs
            tags: List of tag IDs

        Returns:
            Post data including post_id and URL
        """
        self.status = "publishing"
        self.current_task = "publishing to WordPress"

        content = self._get_current_content()
        title = self._extract_title(content)

        # Remove title from content (WordPress handles title separately)
        content_body = content
        if content.startswith(f"# {title}"):
            content_body = content[len(f"# {title}"):].strip()

        html_content = self._markdown_to_html(content_body)

        # Try MCP protocol first
        if await self._check_mcp_support(site_url):
            try:
                self.current_task = "publishing via WordPress MCP"
                result = await self._publish_via_mcp(
                    site_url, username, app_password, title, html_content, status
                )
                result["published_at"] = datetime.utcnow().isoformat()
                save_to_memory(self.session_id, "publish/wordpress", result)
                self.status = "complete"
                self.current_task = "published to WordPress via MCP"
                return result
            except Exception as mcp_error:
                # Log and fall back to REST API
                self.current_task = f"MCP failed ({str(mcp_error)[:50]}), trying REST API"

        # Fall back to REST API
        self.current_task = "publishing via REST API"
        api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"

        post_data = {
            "title": title,
            "content": html_content,
            "status": status,
        }

        if categories:
            post_data["categories"] = categories
        if tags:
            post_data["tags"] = tags

        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                json=post_data,
                auth=(username, app_password),
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

        publish_result = {
            "post_id": result["id"],
            "url": result["link"],
            "edit_url": f"{site_url}/wp-admin/post.php?post={result['id']}&action=edit",
            "status": result["status"],
            "published_at": datetime.utcnow().isoformat(),
            "method": "rest_api"
        }

        # Save publish record
        save_to_memory(self.session_id, "publish/wordpress", publish_result)

        self.status = "complete"
        self.current_task = "published to WordPress"

        return publish_result

    def export_to_html(self, include_styles: bool = True) -> Dict[str, Any]:
        """
        Export content as standalone HTML file.

        Returns:
            HTML content and suggested filename
        """
        self.status = "exporting"
        self.current_task = "exporting to HTML"

        content = self._get_current_content()
        title = self._extract_title(content)
        html_body = self._markdown_to_html(content)

        if include_styles:
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.7;
            color: #333;
            background: #fafafa;
        }}
        article {{
            background: white;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }}
        h2 {{
            color: #2a2a2a;
            font-size: 1.75rem;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #eee;
        }}
        h3 {{
            color: #3a3a3a;
            font-size: 1.35rem;
            margin-top: 2rem;
        }}
        p {{
            margin-bottom: 1.25rem;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 1.25rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
        }}
        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}
        blockquote {{
            border-left: 4px solid #0066cc;
            margin: 1.5rem 0;
            padding: 0.5rem 0 0.5rem 1.5rem;
            color: #555;
            background: #f9f9f9;
            border-radius: 0 4px 4px 0;
        }}
        ul, ol {{
            margin-bottom: 1.25rem;
            padding-left: 1.5rem;
        }}
        li {{
            margin-bottom: 0.5rem;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1.5rem 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 0.75rem;
            text-align: left;
        }}
        th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
        .meta {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <article>
        {html_body}
    </article>
    <footer style="text-align: center; margin-top: 2rem; color: #888; font-size: 0.85rem;">
        Generated by Content Creation Engine
    </footer>
</body>
</html>"""
        else:
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <article>
        {html_body}
    </article>
</body>
</html>"""

        # Generate filename
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in title)
        safe_title = safe_title.replace(' ', '-').lower()[:50]
        filename = f"{safe_title}.html"

        export_result = {
            "html": html,
            "filename": filename,
            "title": title,
            "exported_at": datetime.utcnow().isoformat()
        }

        # Save export record
        save_to_memory(self.session_id, "publish/html", {
            "filename": filename,
            "title": title,
            "exported_at": datetime.utcnow().isoformat()
        })

        self.status = "complete"
        self.current_task = "exported to HTML"

        return export_result

    async def verify_citations(self) -> Dict[str, Any]:
        """
        Verify that citations/links in content are valid.
        """
        self.status = "verifying"
        self.current_task = "verifying citations"

        content = self._get_current_content()

        # Extract URLs from markdown links
        import re
        url_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(url_pattern, content)

        results = {
            "total_links": len(links),
            "valid": [],
            "invalid": [],
            "checked_at": datetime.utcnow().isoformat()
        }

        async with httpx.AsyncClient() as client:
            for text, url in links:
                try:
                    response = await client.head(url, timeout=10.0, follow_redirects=True)
                    if response.status_code < 400:
                        results["valid"].append({"text": text, "url": url})
                    else:
                        results["invalid"].append({
                            "text": text,
                            "url": url,
                            "status": response.status_code
                        })
                except Exception as e:
                    results["invalid"].append({
                        "text": text,
                        "url": url,
                        "error": str(e)
                    })

        save_to_memory(self.session_id, "publish/citation_check", results)

        self.status = "complete"
        return results

    def get_state(self) -> AgentState:
        return AgentState(
            agent_id=self.agent_id,
            agent_type="publisher",
            status=self.status,
            current_task=self.current_task,
            tool_calls=self.tool_calls,
            findings_count=0
        )
