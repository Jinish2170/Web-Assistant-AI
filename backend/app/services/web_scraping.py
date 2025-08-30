import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urljoin, urlparse
import re
from ..core.config import settings

logger = logging.getLogger(__name__)

class WebScrapingService:
    def __init__(self):
        self.max_pages = settings.MAX_SCRAPE_PAGES
        self.timeout = settings.SCRAPE_TIMEOUT
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str, extract_links: bool = True, extract_images: bool = False) -> Dict[str, Any]:
        """Scrape a single URL and extract content"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "url": url,
                        "error": f"HTTP {response.status}",
                        "content": "",
                        "title": None
                    }
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else None
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Extract main content
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
                if main_content:
                    text_content = main_content.get_text()
                else:
                    text_content = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                content = ' '.join(chunk for chunk in chunks if chunk)
                
                result = {
                    "url": url,
                    "title": title_text,
                    "content": content,
                    "word_count": len(content.split()),
                    "metadata": {
                        "status_code": response.status,
                        "content_type": response.headers.get('content-type', ''),
                        "last_modified": response.headers.get('last-modified', ''),
                    }
                }
                
                # Extract links if requested
                if extract_links:
                    links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urljoin(url, href)
                        if self._is_valid_url(absolute_url):
                            links.append({
                                "url": absolute_url,
                                "text": link.get_text().strip(),
                                "title": link.get('title', '')
                            })
                    result["links"] = links
                
                # Extract images if requested
                if extract_images:
                    images = []
                    for img in soup.find_all('img', src=True):
                        src = img['src']
                        absolute_url = urljoin(url, src)
                        images.append({
                            "url": absolute_url,
                            "alt": img.get('alt', ''),
                            "title": img.get('title', '')
                        })
                    result["images"] = images
                
                return result
                
        except asyncio.TimeoutError:
            return {"url": url, "error": "Timeout", "content": "", "title": None}
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {"url": url, "error": str(e), "content": "", "title": None}
    
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently"""
        if not self.session:
            async with self:
                tasks = [self.scrape_url(url, **kwargs) for url in urls[:self.max_pages]]
                return await asyncio.gather(*tasks, return_exceptions=False)
        else:
            tasks = [self.scrape_url(url, **kwargs) for url in urls[:self.max_pages]]
            return await asyncio.gather(*tasks, return_exceptions=False)
    
    async def search_and_scrape(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search Google and scrape the top results"""
        try:
            # Create Google search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={num_results * 2}"
            
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract search result URLs
                search_results = []
                for result in soup.find_all('div', class_='g'):
                    link_tag = result.find('a')
                    if link_tag and link_tag.get('href'):
                        url = link_tag['href']
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        title_tag = result.find('h3')
                        title = title_tag.get_text() if title_tag else ""
                        
                        snippet_tag = result.find('div', class_=['VwiC3b', 's3v9rd'])
                        snippet = snippet_tag.get_text() if snippet_tag else ""
                        
                        if self._is_valid_url(url) and not any(domain in url for domain in ['youtube.com', 'facebook.com', 'twitter.com']):
                            search_results.append({
                                "url": url,
                                "title": title,
                                "snippet": snippet
                            })
                        
                        if len(search_results) >= num_results:
                            break
                
                # Scrape the actual pages
                urls = [result["url"] for result in search_results]
                scraped_results = await self.scrape_multiple(urls, extract_links=False)
                
                # Combine search metadata with scraped content
                for i, scraped in enumerate(scraped_results):
                    if i < len(search_results):
                        scraped.update({
                            "search_title": search_results[i]["title"],
                            "search_snippet": search_results[i]["snippet"],
                            "query": query
                        })
                
                return scraped_results
                
        except Exception as e:
            logger.error(f"Error in search and scrape: {str(e)}")
            return []
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and not a file download"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Skip certain file types
            excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.exe']
            if any(url.lower().endswith(ext) for ext in excluded_extensions):
                return False
            
            # Skip social media and video sites for content scraping
            excluded_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com']
            if any(domain in parsed.netloc.lower() for domain in excluded_domains):
                return False
            
            return True
        except:
            return False
    
    async def get_page_summary(self, url: str) -> str:
        """Get a concise summary of a web page"""
        result = await self.scrape_url(url, extract_links=False, extract_images=False)
        
        if result.get("error"):
            return f"Unable to access {url}: {result['error']}"
        
        content = result.get("content", "")
        title = result.get("title", "")
        
        if not content:
            return f"No content found at {url}"
        
        # Simple summarization - take first few sentences
        sentences = content.split('. ')
        summary_sentences = sentences[:3]  # First 3 sentences
        summary = '. '.join(summary_sentences)
        
        if len(summary) > 500:
            summary = summary[:500] + "..."
        
        return f"**{title}**\n\n{summary}" if title else summary
