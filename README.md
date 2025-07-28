# 🌸 H3ntai Hydra ✨

Nya-llo there! Welcome to H3ntai Hydra, a super cute and helpful script to download and organize your favorite manga and turn them into lovely CBR and CBZ files! 💕

## What is this script? 🤔

This little helper downloads manga from supported websites and then bundles the images into tidy `.cbr` or `.cbz` archive files, which are perfect for reading in comic book reader applications! It's like magic, but for manga! ✨

## How to get started? 🌱

Before you can start downloading, you need to set things up! Don't worry, it's easy peasy!

### 📦 Install Dependencies with `uv`

This project uses `uv` to manage Python packages. If you don't have `uv` installed yet, you can find instructions on their website!

Once `uv` is ready, just run this command in your project directory:

```bash
uv sync
```

This will look at the `requirements.txt` (or `pyproject.toml` if you have one!) and install all the needed Python libraries. Yay! 🎉

### 📚 System Requirements for CBR

If you want to create `.cbr` files (which often use the RAR format), you'll need the `rar` or `unrar` command-line tools installed on your system. The `patoolib` library that the script uses relies on these tools being available!

Depending on your operating system, you might be able to install them using your package manager:

- **Debian/Ubuntu:** `sudo apt-get install rar unrar`
- **macOS (using Homebrew):** `brew install rar unrar`
- **Windows:** You might need to download the command-line tools from the official WinRAR website.

Make sure you can run the `rar` or `unrar` command in your terminal after installation!

### 🕸️ Proxy Configuration (Must for nhentai)

If you want to use a proxy, this script supports using one via environment variables loaded from a `.env` file! 🤫

1.  **Rename `.env.example` to `.env`**: Find the file named `.env.example` in the project root and rename it to just `.env`.
2.  **Set Proxy Variables**: Open the new `.env` file and add or modify the following lines with your proxy details:

    ```dotenv
    use_proxy=enabled
    data_impulse_host='gw.dataimpulse.com:823'
    data_impulse_user=your_proxy_username
    data_impulse_passwd=your_proxy_password
    ```
    Replace `your_proxy_host`, `your_proxy_username`, and `your_proxy_password` with your actual proxy credentials.
3.  **Enable Proxy**: Make sure `use_proxy` is set to `enabled` in the `.env` file to activate the proxy.

Now your script will use the specified proxy when downloading! 🌐

## How to use? 🎀

(✨ Add instructions on how to run your script here! Like `python main.py` and what inputs it expects ✨)

For example:

```bash
python main.py
```

Then the script will guide you with cute messages! 😊

## Have fun reading! 💖

That's it! Now you're all set to download and read your manga in lovely archive formats! If you have any questions or find any little bugs, feel free to ask! Happy reading! 🥰
