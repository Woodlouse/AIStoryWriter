import os
import json
import glob
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
    def _get_next_story_number(title: str) -> int:
        """获取下一个故事序号"""
        pattern = f"Stories/Story_{title.replace(' ', '_')}_*_Score_*.md"
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
            fname = f"Stories/Story_{title.replace(' ', '_')}_{next_num}_Score_{score}"
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