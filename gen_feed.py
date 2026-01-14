import os
import time
import email.utils
import re
from xml.sax.saxutils import escape

try:
    from mutagen import File
except ImportError:
    print("请先安装 mutagen: pip install mutagen")
    exit(1)

# --- Configuration (请修改这里) ---
# 你的 GitHub Pages 基础 URL (注意最后要有斜杠)
BASE_URL = "https://csyuer.github.io/podcast/"
# 音频文件存放的文件夹名称
AUDIO_DIR = "audio"
# 播客标题
PODCAST_TITLE = "我的个人播客"
# 播客描述
PODCAST_DESC = "这是一个基于 GitHub Pages 的简单个人播客。"
# 你的名字
AUTHOR = "Your Name"
# 封面图片 (可选)
IMAGE_URL = BASE_URL + "cover.jpg"
# --- End Configuration ---

def clean_filename(filename):
    """
    清理文件名：
    1. 分离扩展名
    2. 删除空格和半角符号 (只保留 字母、数字、中文、下划线、连字符)
    3. 重新组合
    """
    # 允许保留的文件扩展名
    if not filename.lower().endswith(('.mp3', '.m4a')):
        return filename

    name, ext = os.path.splitext(filename)
    
    # 正则替换：将非单词字符(字母数字下划线)、非中文、非连字符 的字符替换为空
    # \w 包含 [a-zA-Z0-9_]，\u4e00-\u9fa5 是常见汉字范围
    new_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '', name)
    
    return new_name + ext

def sanitize_files():
    """遍历目录并重命名文件"""
    if not os.path.exists(AUDIO_DIR):
        print(f"错误: 找不到文件夹 '{AUDIO_DIR}'")
        return

    print("正在检查并清理文件名...")
    for filename in os.listdir(AUDIO_DIR):
        # 跳过隐藏文件
        if filename.startswith('.'):
            continue
            
        old_path = os.path.join(AUDIO_DIR, filename)
        
        # 仅处理文件
        if os.path.isfile(old_path):
            new_filename = clean_filename(filename)
            
            # 如果文件名发生变化
            if new_filename != filename:
                new_path = os.path.join(AUDIO_DIR, new_filename)
                
                # 防止覆盖已存在的同名文件
                if os.path.exists(new_path):
                    print(f"警告: 目标文件 {new_filename} 已存在，跳过重命名 {filename}")
                else:
                    os.rename(old_path, new_path)
                    print(f"重命名: '{filename}' -> '{new_filename}'")

def get_file_info(filepath):
    """获取文件大小和时长"""
    size = os.path.getsize(filepath)
    try:
        audio = File(filepath)
        duration = int(audio.info.length) if audio and audio.info else 0
    except:
        duration = 0
    return size, duration

def generate_rss():
    # 先执行重命名
    sanitize_files()

    items_xml = ""
    files = []
    
    # 重新读取目录（因为文件名可能变了）
    if not os.path.exists(AUDIO_DIR):
        return

    for f in os.listdir(AUDIO_DIR):
        if f.lower().endswith(('.mp3', '.m4a')):
            files.append(f)
    
    # --- 修改点：按文件名排序 ---
    # reverse=True 表示倒序 (例如 Ep03 在 Ep01 前面)，这样最新的集数会排在 Feed 顶部
    files.sort(reverse=False)

    print(f"检测到 {len(files)} 个音频文件，开始生成 XML...")

    for filename in files:
        filepath = os.path.join(AUDIO_DIR, filename)
        # URL 编码 (虽然我们清理了文件名，但保险起见还是做一个简单的替换)
        file_url = f"{BASE_URL}{AUDIO_DIR}/{filename}"
        
        size, duration = get_file_info(filepath)
        
        # 获取文件修改时间作为发布时间
        mod_time = os.path.getmtime(filepath)
        pub_date = email.utils.formatdate(mod_time, usegmt=True)
        
        # 确定 MIME type
        mime_type = "audio/mpeg" if filename.lower().endswith('.mp3') else "audio/mp4"

        # 生成单集 item
        items_xml += f"""
    <item>
      <title>{escape(filename)}</title>
      <description>{escape(filename)}</description>
      <enclosure url="{file_url}" length="{size}" type="{mime_type}"/>
      <guid isPermaLink="false">{file_url}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:duration>{duration}</itunes:duration>
    </item>"""

    # 生成完整的 RSS XML
    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
  <channel>
    <title>{escape(PODCAST_TITLE)}</title>
    <link>{BASE_URL}</link>
    <description>{escape(PODCAST_DESC)}</description>
    <itunes:author>{escape(AUTHOR)}</itunes:author>
    <itunes:image href="{IMAGE_URL}"/>
    <language>zh-cn</language>
    {items_xml}
  </channel>
</rss>
"""
    
    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_content)
    print("成功生成 feed.xml！")

if __name__ == "__main__":
    generate_rss()