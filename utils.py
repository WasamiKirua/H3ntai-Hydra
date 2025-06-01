import asyncio
import aiohttp
import os
import shutil
import zipfile
import patoolib
from rich import print
from rich.console import Console
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from natsort import natsorted
from pathlib import Path

dest_fold = 'data'
load_dotenv()
console = Console()

proxy_host = os.getenv('data_impulse_host')
proxy_user = os.getenv('data_impulse_user')
proxy_passwd = os.getenv('data_impulse_passwd')

def make_cbr_cbz_mangaforfree(hentai_name):
    print(":compression:", ":compression:", "[bold magenta]CBR & CBZ[/bold magenta]!", ":compression:", ":compression:")
    print('\n')
    compression_type = input("Compression Type (Ex: cbr, cbz): ").lower()
    
    if compression_type not in ['cbr', 'cbz']:
        compression_type = 'cbz'

    # Copy cover art if exists
    archive_path = f'data/{hentai_name}/{hentai_name}.{compression_type}'
    sorted_items = natsorted(Path(f'data/{hentai_name}/chapters').iterdir())
    dst_dir = f'data/{hentai_name}/temp/{hentai_name}/chapters'

    # Create temporary directory for organizing files
    os.makedirs(dst_dir, exist_ok=True)

    for dir_name in sorted_items:
        if dir_name.is_dir():
            shutil.copytree(dir_name, os.path.join(dst_dir, dir_name.name))
            print(f"[bold green]Chapter moved to tmp folder:[/bold green] {archive_path}", ":ok:")

    if compression_type == 'cbz':
        image_files = []
        for root, _, files in os.walk(dst_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    image_files.append(Path(root) / file)

        # Sort files naturally by chapter and page number
        sorted_image_files = natsorted(image_files)

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_path in enumerate(sorted_image_files):
                # Create a new filename for the flattened archive
                # Using a simple sequential index for now. 
                # More sophisticated naming (e.g., based on chapter/page) could be added here.
                new_filename = f'{i+1:04d}{file_path.suffix}'
                zipf.write(file_path, new_filename)
        print(f"[bold green]CBZ file created:[/bold green] {archive_path}", ":ok:")

    elif compression_type == 'cbr':
        patoolib.create_archive(archive_path, [dst_dir])
        print(f"[bold green]CBR file created:[/bold green] {archive_path}", ":ok:")
    shutil.rmtree(dst_dir)
    print(f"[bold green]Tmp folder removed:[/bold green] {archive_path}", ":ok:")
    

def make_cbr_cbz_nhentai(hentai_name):
    print(":compression:", ":compression:", "[bold magenta]CBR & CBZ[/bold magenta]!", ":compression:", ":compression:")
    print('\n')
    compression_type = input("Compression Type (Ex: cbr, cbz): ").lower()
    
    if compression_type not in ['cbr', 'cbz']:
        compression_type = 'cbz'

    # Create temporary directory for organizing files
    temp_dir = f'data/{hentai_name}/temp/{hentai_name}'
    os.makedirs(temp_dir, exist_ok=True)

    # Copy cover art if exists
    archive_path = f'data/{hentai_name}/{hentai_name}.{compression_type}'
    
    if os.path.exists(f'data/{hentai_name}/1.jpg'):
        shutil.move(f'data/{hentai_name}/1.jpg', f'data/{hentai_name}/temp/{hentai_name}/1-cover.jpg')
    
    src_dir = f'data/{hentai_name}/images'
    dst_dir = f'data/{hentai_name}/temp/{hentai_name}'

    for file in os.listdir(src_dir):
        shutil.copy2(os.path.join(src_dir, file), dst_dir)
    
    # Create zip file
    try:
        if compression_type == 'cbz':
            sorted_items = natsorted(Path(dst_dir).iterdir())
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                source_dir = Path(temp_dir)
                for file in sorted_items:
                    if file.is_file():
                        zipf.write(file, file.relative_to(source_dir))
            print(f":compression:", "[bold green]CBZ file created:[/bold green] {archive_path}", ":ok:")
        elif compression_type == 'cbr':
            patoolib.create_archive(archive_path, [temp_dir])
            print(f":compression:", "[bold green]CBR file created:[/bold green] {archive_path}", ":ok:")
        shutil.rmtree(temp_dir)
        print(f"[bold green]Tmp folder removed:[/bold green] {archive_path}", ":ok:")

    except Exception as e:
        print(f"[bold red]Error creating zip file: {e}[/bold red]")

async def process_images_nhentai(browser, semaphore, hentai_name, imgs_list):
    async with semaphore:
        page = None
        try:
            page = await browser.new_page()
            for url in imgs_list:
                print(url)
                await page.goto(url)

                img_locators = await page.locator('a img').all() # Increased timeout and simplified locator
                
                if img_locators:
                    # Loop through all img
                    for img_locator in img_locators:
                        img_url = await img_locator.get_attribute('src')
                        if 'nhentai.net' in img_url:
                            print(f"Processing: {img_url}")
                            max_attempts = 3
                            for attempt in range(1, max_attempts + 1):
                                try:
                                    await asyncio.sleep(1) # Let's be kind
                                    print(f"[bold yellow]Downloading IMG:[/bold yellow] {img_url} (Attempt {attempt}/{max_attempts})", ":hourglass:")
                                    async with aiohttp.ClientSession() as session:

                                        async with session.get(img_url) as response:
                                            if response.status == 200:
                                                img_data = await response.read()
                                                # Extract filename from URL
                                                filename = img_url.split('/')[-1]
                                                # Ensure the filename has a proper image extension if needed, or handle cases without extensions
                                                if '.' not in filename: # Basic check, might need more robust handling
                                                    # Attempt to get content type and determine extension
                                                    content_type = response.headers.get('Content-Type')
                                                    if content_type and 'image' in content_type:
                                                         # Simple mapping, could be extended
                                                        extensions = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif', 'image/webp': '.webp'}
                                                        ext = extensions.get(content_type)
                                                        if ext:
                                                            filename += ext
                                                    else:
                                                         # Fallback if content type is not helpful, or handle as error
                                                        filename += '.bin' # Or skip/log error
                                                img_path = os.path.join(f'data/{hentai_name}/images', filename)
                                                with open(img_path, 'wb') as f:
                                                    f.write(img_data)
                                                print(f"[bold green]IMG saved:[/bold green] {img_path}", ":ok:")
                                                break # Exit retry loop on success
                                            else:
                                                print(f"[bold yellow]Download failed with status code {response.status}:[/bold yellow] {url}")
                                except Exception as e:
                                    print(f"[bold red]Error downloading {url}:[/bold red] {e}")
                                if attempt < max_attempts:
                                    print(f"[bold yellow]Retrying in 5 seconds...[/bold yellow]", ":hourglass:")
                                    await asyncio.sleep(5) # Wait before retrying
                                else:
                                    print(f"[bold red]Failed downloading {url} after {max_attempts} attempts.[/bold red]", ":ko:")
                            
                else:
                    print(f"[bold red]Could not find any images with locator 'a img' on {url}[/bold red]")
        except Exception as e:
            print(f"Error processing {url}: {e}") # Added url to error message
        finally:
            if page:
                await page.close()
                make_cbr_cbz_nhentai(hentai_name)

async def process_images_mangaforfree(browser, semaphore, hentai_name, url, chapter_num):
    async with semaphore:
        page = None
        try:
            page = await browser.new_page()
            print("[bold white]Retrieving IMGs URLs for:[/bold white]", f"[magenta]{url}[/magenta]", ":vampire:")
            print('\n')
            await page.goto(url)
            img_locators = await page.locator('img').all() # Increased timeout and simplified locator

            if img_locators:
                    # Uncommented and corrected loop
                    for img_locator in img_locators:
                        img_url = await img_locator.get_attribute('src')
                        if 'mangaforfree.net' in img_url and 'LOGO' not in img_url:
                            print(f"Processing: {img_url}")
                            max_attempts = 3
                            for attempt in range(1, max_attempts + 1):
                                try:
                                    await asyncio.sleep(2) # Let's be kind
                                    print(f"[bold yellow]Downloading IMG:[/bold yellow] {img_url} (Attempt {attempt}/{max_attempts})", ":hourglass:")
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(img_url) as response:
                                            if response.status == 200:
                                                img_data = await response.read()
                                                # Extract filename from URL
                                                filename = img_url.split('/')[-1]
                                                # Ensure the filename has a proper image extension if needed, or handle cases without extensions
                                                if '.' not in filename: # Basic check, might need more robust handling
                                                    # Attempt to get content type and determine extension
                                                    content_type = response.headers.get('Content-Type')
                                                    if content_type and 'image' in content_type:
                                                         # Simple mapping, could be extended
                                                        extensions = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif', 'image/webp': '.webp'}
                                                        ext = extensions.get(content_type)
                                                        if ext:
                                                            filename += ext
                                                    else:
                                                         # Fallback if content type is not helpful, or handle as error
                                                        filename += '.bin' # Or skip/log error
                                                img_path = os.path.join(f'data/{hentai_name}/chapters/{chapter_num}', filename)
                                                with open(img_path, 'wb') as f:
                                                    f.write(img_data)
                                                print(f"[bold green]IMG saved:[/bold green] {img_path}", ":ok:")
                                                break # Exit retry loop on success
                                            else:
                                                print(f"[bold yellow]Download failed with status code {response.status}:[/bold yellow] {url}")
                                except Exception as e:
                                    print(f"[bold red]Error downloading {url}:[/bold red] {e}")
                                if attempt < max_attempts:
                                    print(f"[bold yellow]Retrying in 5 seconds...[/bold yellow]", ":hourglass:")
                                    await asyncio.sleep(5) # Wait before retrying
                                else:
                                    print(f"[bold red]Failed downloading {url} after {max_attempts} attempts.[/bold red]", ":ko:")
        except Exception as e:
            print(f"Error processing {url}: {e}")
        finally:
            if page:
                await page.close()
                make_cbr_cbz_mangaforfree(hentai_name)

async def hentai_net(url, num_page, hentai_name):
    async with async_playwright() as p:
        if os.getenv('use_proxy') == 'enabled':
            print("[bold green](Images URLs) Proxy Enabled![/bold green]", ":spider_web:")
            print('\n')
            browser = await p.chromium.launch(
                proxy={
                    'server': f'{proxy_host}',
                    'username': f'{proxy_user}',
                    'password': f'{proxy_passwd}'
                }
            )
        else:
            print(":no_entry:", "[bold red](Images URLs) Proxy Disabled![/bold red]", ":spider_web:")
            print('\n')
            browser = await p.chromium.launch()

        semaphore = asyncio.Semaphore(3) # Limit to 1 concurrent tasks
        tasks = []

        # Build Folders
        hentai_name = hentai_name.replace(' ', '')
        os.makedirs(dest_fold, exist_ok=True)
        os.makedirs(f'{dest_fold}/{hentai_name}', exist_ok=True)
        os.makedirs(f'{dest_fold}/{hentai_name}/images', exist_ok=True)

        imgs_list = []
        
        for page in range(1, int(num_page)):
            imgs_list.append(f'{url}{page}')

        tasks.append(asyncio.create_task(process_images_nhentai(browser, semaphore, hentai_name, imgs_list)))

        await asyncio.gather(*tasks)
        await browser.close()

async def mangaforfree(chapters_list, hentai_name):
    async with async_playwright() as p:

        print(hentai_name)

        if os.getenv('use_proxy') == 'enabled':
            print("[bold green](Images URLs) Proxy Enabled![/bold green]", ":spider_web:")
            print('\n')
            browser = await p.chromium.launch(
                proxy={
                    'server': f'{proxy_host}',
                    'username': f'{proxy_user}',
                    'password': f'{proxy_passwd}'
                }
            )
        else:
            print(":no_entry:", "[bold red](Images URLs) Proxy Disabled![/bold red]", ":spider_web:")
            print('\n')
            browser = await p.chromium.launch()

        semaphore = asyncio.Semaphore(1) # Limit to 1 concurrent tasks to better retriever > 1 might cause issue
        tasks = []

        # Build Folders
        
        hentai_name = hentai_name.replace(' ', '')
        os.makedirs(dest_fold, exist_ok=True)
        os.makedirs(f'{dest_fold}/{hentai_name}', exist_ok=True)
        os.makedirs(f'{dest_fold}/{hentai_name}/chapters', exist_ok=True)

        for url in chapters_list:
            chapter_num = url.split('/')[5]

            if os.path.exists(f'{dest_fold}/{hentai_name}/chapters/{chapter_num}'):
                console.print(":hot_face:","[bold magenta]Chapter already processed! Skipping[/bold magenta]", ":hot_face:")
                continue
            else:
                os.makedirs(f'{dest_fold}/{hentai_name}/chapters/{chapter_num}', exist_ok=True)
                tasks.append(asyncio.create_task(process_images_mangaforfree(browser, semaphore, hentai_name, url, chapter_num)))

        await asyncio.gather(*tasks)
        await browser.close()

