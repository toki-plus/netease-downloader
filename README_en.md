# Netease Downloader: A High-Quality/Lossless Music Downloader for Netease Cloud Music

[简体中文](./README.md) | [English](./README_en.md)

[![GitHub stars](https://img.shields.io/github/stars/toki-plus/netease-downloader?style=social)](https://github.com/toki-plus/netease-downloader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/toki-plus/netease-downloader?style=social)](https://github.com/toki-plus/netease-downloader/network/members)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/toki-plus/netease-downloader/pulls)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

**`Netease Downloader` is an elegant and efficient downloader for Netease Cloud Music, crafted for music enthusiasts who demand the ultimate in audio quality and user experience.** It provides a modern graphical interface that integrates **searching, parsing, multi-quality downloading, and metadata tagging** into a single application, allowing you to effortlessly acquire and manage your favorite music.

This project aims to address the shortcomings of traditional download tools—such as outdated interfaces, limited functionality, and cumbersome login processes—by offering a comprehensive, all-in-one solution with an intuitive workflow.

<p align="center">
  <a href="https://www.bilibili.com" target="_blank">
    <img src="./images/cover_demo.png" alt="Click to watch the demo video on Bilibili (Coming Soon)" width="800"/>
  </a>
  <br>
  <em>(Click the cover to watch the HD demo video on Bilibili)</em>
</p>

---

## ✨ Core Features

This project delivers a seamless music acquisition experience through four core modules:

### 🎵 Multi-Dimensional Parsing Engine

-   **Keyword Search**: Quickly search for songs by title or artist, with results displayed in a clear, sortable table.
-   **Precise Track Parsing**: Supports direct parsing of a specific song's detailed information by inputting its ID or URL.
-   **Batch Playlist/Album Parsing**: Parse all songs within a playlist or album with a single ID/URL, making batch operations effortless.

### 💎 High-Quality & Lossless Download

-   **Multiple Quality Options**: Choose from a wide range of audio qualities, including `Standard`, `Extra High`, `Lossless`, `Hi-Res`, and even immersive formats like `Surround Sound` and `Master Audio`.
-   **Multi-threaded Downloading**: The backend utilizes a multi-threaded architecture for efficient background downloading, ensuring the UI remains responsive, complete with a real-time progress bar.
-   **Intelligent File Naming**: Automatically generates filenames in the "Artist - Title" format and sanitizes special characters for universal compatibility.

### 🏷️ Automated Metadata Tagging

-   **ID3 Tag Injection**: After downloading, the tool automatically writes essential metadata—such as **title, artist, album, cover art, and track number** (ID3 Tags)—into the music file.
-   **Embedded Album Art**: Automatically fetches and embeds high-resolution album art, ensuring your music library looks clean and professional in any player.
-   **Multi-Format Support**: Perfectly supports writing metadata to popular audio formats like `MP3`, `FLAC`, and `M4A`.

### 🖥️ Modern GUI

-   **QR Code Login**: Integrated QR code login allows you to log in securely by scanning with the Netease Cloud Music app, automatically managing cookies and eliminating tedious manual input.
-   **Intuitive Workflow**: The interface is cleanly divided into four functional tabs: `Search`, `Parse Track`, `Parse List/Album`, and `Download`, providing a clear and logical user flow.
-   **Real-time Info Preview**: Instantly preview album art, detailed track information, and lyrics after parsing or selecting a song.
-   **Cross-Platform Design**: Built with `PyQt5`, offering excellent potential for cross-platform compatibility.

## 📸 Screenshots

<p align="center">
  <img src="./images/cover_software_main.png" alt="Main Software Interface" width="800"/>
  <br>
  <em>Main Software Interface: Integrates core functions like search, parsing, and downloading for an intuitive user experience.</em>
</p>

## 🚀 Quick Start

### System Requirements

1.  **OS**: Windows / macOS / Linux (thoroughly tested on Windows).
2.  **Python**: 3.8 or higher.

### Installation & Launch

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/toki-plus/netease-downloader.git
    cd netease-downloader
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python main.py
    ```

## 📖 Usage Guide

1.  **First-Time Login (Recommended)**:
    -   Click on `Login` -> `QR Code Login` from the menu bar.
    -   Scan the pop-up QR code with your Netease Cloud Music mobile app and confirm the login.
    -   Upon success, the status bar will display "Status: Logged In," enabling you to download VIP songs and higher-quality audio.

2.  **Search for Songs**:
    -   Select the `Search` tab, enter your keywords, and click the `Search` button.
    -   Results will appear in the table below.

3.  **Parse & Preview**:
    -   **Double-click** any song in the results table. The application will automatically switch to the `Parse Track` mode and begin parsing that song.
    -   Once complete, you can preview the song's cover art, detailed information, and lyrics in the panels below.

4.  **Download a Song**:
    -   Switch to the `Download` tab.
    -   Enter the song ID or URL you wish to download (you can copy it from the preview section or official Netease sources).
    -   Select your desired **audio quality**.
    -   Click the `Download` button. The progress bar in the status bar will show the download progress.
    -   After completion, click `Open Folder` to view your downloaded music file.

5.  **Batch Downloading**:
    -   Select the `Parse List/Album` tab and enter the playlist or album ID/URL.
    -   Click `Parse List`. All songs from the list will populate the results table.
    -   You can then double-click individual songs to preview or switch to the `Download` mode to download them by manually entering their IDs.

---

<p align="center">
  <strong>For custom development or technical inquiries, please connect via:</strong>
</p>
<table align="center">
  <tr>
    <td align="center">
      <img src="./images/wechat.png" alt="WeChat QR Code" width="200"/>
      <br />
      <sub><b>WeChat</b></sub>
      <br />
      <sub>ID: toki-plus (Note: "GitHub Customization")</sub>
    </td>
    <td align="center">
      <img src="./images/gzh.png" alt="Public Account QR Code" width="200"/>
      <br />
      <sub><b>Public Account</b></sub>
      <br />
      <sub>Scan for tech articles</sub>
    </td>
  </tr>
</table>

## 📂 My Other Open-Source Projects

-   **[AI-Trader-For-MT4](https://github.com/toki-plus/ai-trader-for-mt4)**: A revolutionary open-source framework that transforms a Large Language Model (LLM) into an autonomous trading agent for the MetaTrader 4 (MT4) platform.
-   **[Auto USPS Tracker](https://github.com/toki-plus/auto-usps-tracker)**: An efficient USPS bulk package tracker for e-commerce sellers, featuring anti-blocking scraping and formatted Excel report generation.
-   **[AI Mixed Cut](https://github.com/toki-plus/ai-mixed-cut)**: A groundbreaking AI content re-creation engine that deconstructs viral videos into a creative library and automatically generates new, original videos using a "Deconstruct-Reconstruct" model.
-   **[AI Video Workflow](https://github.com/toki-plus/ai-video-workflow)**: A fully automated AI-native video generation pipeline, integrating Text-to-Image, Image-to-Video, and Text-to-Music models to create AIGC short videos with one click.
-   **[AI Highlight Clip](https://github.com/toki-plus/ai-highlight-clip)**: An AI-driven intelligent clipping tool that automatically analyzes and extracts "highlight moments" from long-form videos and generates viral titles.
-   **[AI TTV Workflow](https://github.com/toki-plus/ai-ttv-workflow)**: An AI-powered Text-to-Video tool that automatically converts any script into a short video with voiceover, subtitles, and a cover, supporting script extraction/re-creation/translation.
-   **[AB Video Deduplicator](https://github.com/toki-plus/AB-Video-Deduplicator)**: Utilizes an innovative "High-Framerate Frame-Mixing" technique to fundamentally alter a video's data fingerprint, designed to bypass originality detection/deduplication mechanisms on major short-video platforms.
-   **[Video Mover](https://github.com/toki-plus/video-mover)**: A fully automated content creation pipeline that monitors and downloads videos, performs multi-dimensional deduplication, generates AI titles, and publishes to multiple platforms with one click.

## 🤝 Contributing

Contributions of any kind are welcome! If you have ideas for new features, found a bug, or have any suggestions for improvement, please:
-   Submit an [Issue](https://github.com/toki-plus/ai-trader-for-mt4/issues) to start a discussion.
-   Fork this repository and submit a [Pull Request](https://github.com/toki-plus/ai-trader-for-mt4/pulls).

If this project has been helpful to you, please consider giving it a ⭐!

## 📜 License

This project is open-sourced under the MIT License. See the [LICENSE](LICENSE) file for details.