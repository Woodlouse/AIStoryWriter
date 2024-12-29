import os
import json
import glob
import re
import Writer.Config

class FileHandler:
    @staticmethod
    def load_prompt(prompt_path: str) -> str:
        """加载用户提供的故事提示文件"""
        if prompt_path is None:
            raise Exception("No Prompt Provided")
        with open(prompt_path, "r") as f:
            return f.read()

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除或替换非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的合法文件名
        """
        # 替换或移除Windows和Unix系统中的非法字符
        # 移除: / \ : * ? " < > | 和其他特殊字符
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
        # 将空格替换为下划线
        sanitized = re.sub(r'\s+', '_', sanitized)
        # 确保文件名不为空
        if not sanitized:
            sanitized = "untitled"
        return sanitized

    @staticmethod
    def _get_next_story_number(title: str) -> int:
        """获取下一个故事序号"""
        sanitized_title = FileHandler._sanitize_filename(title)
        pattern = f"Stories/Story_{sanitized_title}_*_Score_*.md"
        existing_files = glob.glob(pattern)
        if not existing_files:
            return 1
        
        numbers = []
        for file in existing_files:
            # 从文件名中提取序号
            try:
                # Story_标题_1_Score_85.md
                parts = file.split('_')
                for i, part in enumerate(parts):
                    if part.isdigit() and i < len(parts)-1 and parts[i+1] == "Score":
                        numbers.append(int(part))
            except:
                continue
        
        return max(numbers, default=0) + 1

    @staticmethod
    def save_story(title: str, story_body: str, stats: str, outline: str, story_info: dict):
        """保存生成的故事和相关信息到文件"""
        os.makedirs("Stories", exist_ok=True)

        # 获取评分
        score = story_info.get("Score", "0")
        
        # 如果没有指定输出文件名，则自动生成
        if Writer.Config.OPTIONAL_OUTPUT_NAME == "":
            # 获取下一个序号
            next_num = FileHandler._get_next_story_number(title)
            sanitized_title = FileHandler._sanitize_filename(title)
            fname = f"Stories/Story_{sanitized_title}_{next_num}_Score_{score}"
        else:
            fname = Writer.Config.OPTIONAL_OUTPUT_NAME

        # 保存故事主体和元数据
        with open(f"{fname}.md", "w", encoding="utf-8") as f:
            output = f"""
{stats}

---

评分: {score}/100
评价: {story_info.get("Summary", "无评价")}

---

Note: An outline of the story is available at the bottom of this document.
Please scroll to the bottom if you wish to read that.

---
# {title}

{story_body}


---
# Outline
```
{outline}
```
"""
            f.write(output)

        # 保存JSON格式的故事信息
        with open(f"{fname}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(story_info, indent=4))
            
        # 清理临时文件
        FileHandler.clean_temp_files(title)

    @staticmethod
    def save_temp_chapter_outline(chapter_num: int, chapter_outline: str, title: str):
        """保存章节大纲的临时文件"""
        os.makedirs("Temp", exist_ok=True)
        sanitized_title = FileHandler._sanitize_filename(title)
        with open(f"Temp/Chapter_{sanitized_title}_{chapter_num}_Outline.txt", "w", encoding="utf-8") as f:
            f.write(chapter_outline)

    @staticmethod
    def save_temp_story_info(title: str, story_info: dict):
        """保存故事信息的临时文件"""
        os.makedirs("Temp", exist_ok=True)
        sanitized_title = FileHandler._sanitize_filename(title)
        with open(f"Temp/Story_{sanitized_title}_Info.json", "w", encoding="utf-8") as f:
            json.dump(story_info, f, indent=4, ensure_ascii=False)

    @staticmethod
    def load_temp_chapter_outline(chapter_num: int, title: str) -> str:
        """加载章节大纲的临时文件"""
        sanitized_title = FileHandler._sanitize_filename(title)
        try:
            with open(f"Temp/Chapter_{sanitized_title}_{chapter_num}_Outline.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @staticmethod
    def load_temp_story_info(title: str) -> dict:
        """加载故事信息的临时文件"""
        sanitized_title = FileHandler._sanitize_filename(title)
        try:
            with open(f"Temp/Story_{sanitized_title}_Info.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    def clean_temp_files(title: str):
        """清理临时文件"""
        sanitized_title = FileHandler._sanitize_filename(title)
        temp_pattern = f"Temp/*{sanitized_title}*"
        for file in glob.glob(temp_pattern):
            try:
                os.remove(file)
            except:
                pass 