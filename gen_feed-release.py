import time
import email.utils
from xml.sax.saxutils import escape

# --- Configuration (方案B专用配置) ---
# 修改为你的 Release 下载基础路径
# 格式: https://github.com/用户名/仓库名/releases/download/标签名/
RELEASE_BASE_URL = "https://github.com/csyuer/podcast/releases/download/Audio/"

PODCAST_TITLE = "我的个人播客 (Release版)"
PODCAST_DESC = "使用 GitHub Releases 托管的大容量播客"
AUTHOR = "Your Name"
IMAGE_URL = "https://csyuer.github.io/podcast/cover.jpg"

# 在这里列出你已经上传到 Release 的文件名（建议按你想要的顺序排列）
# 以后每在 Release 里多传一个，就在这里加一行
AUDIO_FILES = [
    "Counting Stars - OneRepublic.mp3",
    "Enemy (from the series Arcane League of Legends) - Imagine Dragons_JID_双城之战_英雄联盟.mp3",
]
# --- End Configuration ---

def generate_rss():
    items_xml = ""
    base_time = time.time()

    print(f"开始为 {len(AUDIO_FILES)} 个 Release 文件生成 Feed...")

    for index, filename in enumerate(AUDIO_FILES):
        # 拼接 Release 下载链接
        file_url = f"{RELEASE_BASE_URL}{filename}"
        
        # 注意：由于文件不在本地，脚本无法自动获取文件大小和时长
        # 播客协议里这两个参数不是强制精确的，我们可以填 0 或 默认值
        # 如果你追求完美，可以手动输入大小，或者先在本地运行旧脚本获取数值
        size = "10485760"  # 默认填 10MB 左右的字节数，不影响播放
        duration = "00:00:00"

        fake_time = base_time - (index * 60)
        pub_date = email.utils.formatdate(fake_time, usegmt=True)
        
        mime_type = "audio/mpeg" if filename.lower().endswith('.mp3') else "audio/mp4"

        items_xml += f"""
    <item>
      <title>{escape(filename)}</title>
      <description>{escape(filename)}</description>
      <enclosure url="{file_url}" length="{size}" type="{mime_type}"/>
      <guid isPermaLink="false">{file_url}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:duration>{duration}</itunes:duration>
    </item>"""

    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
  <channel>
    <title>{escape(PODCAST_TITLE)}</title>
    <link>{RELEASE_BASE_URL}</link>
    <description>{escape(PODCAST_DESC)}</description>
    <itunes:author>{escape(AUTHOR)}</itunes:author>
    <itunes:image href="{IMAGE_URL}"/>
    <language>zh-cn</language>
    {items_xml}
  </channel>
</rss>
"""
    with open("feed-release.xml", "w", encoding="utf-8") as f:
        f.write(rss_content)
    print("成功生成 feed-release.xml！请 git push 到 GitHub 触发更新。")

if __name__ == "__main__":
    generate_rss()