import os
import asyncio
from rich import print
from rich.console import Console
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from utils import hentai_net, mangaforfree, make_cbr_cbz_mangaforfree

async def main():
    load_dotenv()
    console = Console()

    proxy_host = os.getenv('data_impulse_host')
    proxy_user = os.getenv('data_impulse_user')
    proxy_passwd = os.getenv('data_impulse_passwd')

    print(":sweat_droplets:", ":sweat_droplets:", "[bold magenta]from H3ntai-Hydra[/bold magenta]!", ":sweat_droplets:", ":sweat_droplets:")
    print('\n')
    console.print("Provide URL Ex: https://nhentai.net/g/27024", style="bold white")
    console.print("[bold magenta]Supported:[/bold magenta]", ":hot_face:","https://nhentai.net",":hot_face:",style="bold white")
    console.print("[bold magenta]Supported:[/bold magenta]", ":hot_face:","https://mangaforfree.net",":hot_face:",style="bold white")
    print('\n')
    manga_url = input("URL: ").lower()

    print("[bold white]Parsing URL:[/bold white]", f"[magenta]{manga_url}[/magenta]")
    print('\n')

    async with async_playwright() as p:
        # Load proxy vars if enabled
        if os.getenv('use_proxy') == 'enabled':
            print("[bold green](Volumes URLs) Proxy Enabled![/bold green]", ":spider_web:")
            print('\n')
            browser = await p.chromium.launch(
                proxy={
                    'server': f'{proxy_host}',
                    'username': f'{proxy_user}',
                    'password': f'{proxy_passwd}'
                }
            )
        else:
            print(":no_entry:", "[bold red](Volumes URLs) Proxy Disabled![/bold red]", ":spider_web:")
            print('\n')
            browser = await p.chromium.launch()

        page = await browser.new_page()
        
        await page.goto(manga_url)

        # Here logic for nhentai.net
        if 'nhentai.net' in manga_url:
            try:
                # Locate the element containing the pretty title
                pretty_title_element = page.locator("span.pretty").first
                if pretty_title_element:
                    hentai_name = await pretty_title_element.text_content()
                    print(f"[bold white]Hentai Name:[/bold white] [magenta]{hentai_name}[/magenta]")
                else:
                    hentai_name = "Unknown Title"
                    print("[bold red]Could not find pretty title element. Setting to Unknown Title.[/bold red]")
            except Exception as e:
                hentai_name = "Unknown Title"
                print(f"[bold red]An error occurred while extracting pretty title: {e}. Setting to Unknown Title.[/bold red]")

            # Locate the element containing the page count
            try:
                pages_element = page.locator("div.tag-container:has-text('Pages:') span.tags span.name").first
                if pages_element:
                    page_count = await pages_element.text_content()
                    print(f"[bold white]Pages found:[/bold white] [magenta]{page_count}[/magenta]")
                    print('\n')
                else:
                    print("[bold red]Could not find pages element.[/bold red]")
            except Exception as e:
                print(f"[bold red]An error occurred while extracting page count: {e}[/bold red]")

        # Here logic for Mangaforfree
        else:
            try:
                # Use evaluate to get only the text content directly within the h1 tag
                hentai_name = await page.evaluate("""
                    () => {
                        const h1 = document.querySelector('h1');
                        if (!h1) return null;
                        let text = '';
                        // Iterate through child nodes and collect text from text nodes
                        h1.childNodes.forEach(node => {
                            if (node.nodeType === Node.TEXT_NODE) {
                                text += node.textContent;
                            }
                        });
                        return text.trim(); // Trim whitespace
                    }
                """)
                if hentai_name:
                    print(f"[bold white]Title found (from h1):[/bold white] [magenta]{hentai_name}[/magenta]")
                else:
                    hentai_name = "Unknown Title"
                    print("[bold red]Could not find h1 element or extract title text. Setting to Unknown Title.[/bold red]")
            except Exception as e:
                hentai_name = "Unknown Title"
                print(f"[bold red]An error occurred while extracting h1 title: {e}. Setting to Unknown Title.[/bold red]")
            
            # Get chapters
            try:
                # Explicitly wait for at least one chapter link to appear
                print("Waiting for chapter links to load...")
                await page.locator('li.wp-manga-chapter a').first.wait_for()
                print("Chapter links locator found. Extracting all links...")

                # Locate all <a> tags within li.wp-manga-chapter and get their href
                # Added timeout to wait longer for the elements to load
                chapter_link_locators = await page.locator('li.wp-manga-chapter a').all()
                chapter_links = []
                
                if chapter_link_locators:
                    print(f"Found {len(chapter_link_locators)} chapter link(s).")
                    for link_locator in chapter_link_locators:
                        href = await link_locator.get_attribute('href')
                        if href:
                            if 'raw' not in href:
                                chapter_links.append(href)
                    chapters_list = list(reversed(chapter_links))
                print(f"[bold white]Extracted Chapter Links:[/bold white]")
                
            except Exception as e:
                print(f"[bold red]An error occurred while extracting chapter links: {e}[/bold red]")

    await browser.close()

    # Call the async function
    if 'nhentai.net' in manga_url:
        await hentai_net(manga_url, page_count, hentai_name)
    else:
        await mangaforfree(chapters_list, hentai_name)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
    