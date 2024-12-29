import time
from typing import List, Dict, Tuple

import Writer.Config
import Writer.Interface.Wrapper
import Writer.PrintUtils
import Writer.Chapter.ChapterDetector
import Writer.Chapter.ChapterGenerator
import Writer.Scrubber
import Writer.Statistics
import Writer.OutlineGenerator
import Writer.StoryInfo
import Writer.NovelEditor
import Writer.Translator
import Writer.Utils.FileHandler

class StoryGenerator:
    def __init__(self, interface: Writer.Interface.Wrapper.Interface, logger: Writer.PrintUtils.Logger):
        self.interface = interface
        self.logger = logger
        self.start_time = time.time()
        self.story_info: Dict = {}
        self.title: str = ""

    def _init_story_info(self, prompt: str, outline: str):
        """初始化故事信息"""
        messages = []
        messages.append(self.interface.BuildUserQuery(outline))
        info = Writer.StoryInfo.GetStoryInfo(self.interface, self.logger, messages)
        self.title = info["标题"]
        self.story_info.update({
            "Title": info["标题"],
            "Summary": info["摘要"],
            "Tags": info["标签"],
            "Score": info["整体评分"],
            "BasePrompt": prompt
        })
        # 保存初始故事信息
        Writer.Utils.FileHandler.FileHandler.save_temp_story_info(self.title, self.story_info)

    def generate(self, prompt: str) -> Tuple[str, Dict]:
        """生成故事的主要流程"""
        # 如果需要翻译提示，先进行翻译
        if Writer.Config.TRANSLATE_PROMPT_LANGUAGE != "":
            prompt = Writer.Translator.TranslatePrompt(
                self.interface, self.logger, prompt, Writer.Config.TRANSLATE_PROMPT_LANGUAGE
            )

        # 生成大纲
        outline, elements, rough_chapter_outline, base_context = Writer.OutlineGenerator.GenerateOutline(
            self.interface, self.logger, prompt, Writer.Config.OUTLINE_QUALITY
        )
        
        # 初始化故事信息
        self._init_story_info(prompt, outline)
        
        # 更新故事信息
        self.story_info.update({
            "Outline": outline,
            "StoryElements": elements,
            "RoughChapterOutline": rough_chapter_outline,
            "BaseContext": base_context
        })
        Writer.Utils.FileHandler.FileHandler.save_temp_story_info(self.title, self.story_info)

        # 检测章节数量
        self.logger.Log("Detecting Chapters", 5)
        messages = [self.interface.BuildUserQuery(outline)]
        num_chapters: int = Writer.Chapter.ChapterDetector.LLMCountChapters(
            self.interface, self.logger, self.interface.GetLastMessageText(messages)
        )
        self.logger.Log(f"Found {num_chapters} Chapter(s)", 5)

        # 生成每章的详细大纲
        chapter_outlines: List[str] = []
        if Writer.Config.EXPAND_OUTLINE:
            for chapter in range(1, num_chapters + 1):
                # 尝试从临时文件加载
                chapter_outline = Writer.Utils.FileHandler.FileHandler.load_temp_chapter_outline(chapter, self.title)
                if not chapter_outline:
                    chapter_outline, messages = Writer.OutlineGenerator.GeneratePerChapterOutline(
                        self.interface, self.logger, chapter, outline, messages
                    )
                    # 保存到临时文件
                    Writer.Utils.FileHandler.FileHandler.save_temp_chapter_outline(chapter, chapter_outline, self.title)
                chapter_outlines.append(chapter_outline)

        # 创建完整大纲
        detailed_outline: str = ""
        for chapter in chapter_outlines:
            detailed_outline += chapter
        mega_outline: str = f"""
# Base Outline
{elements}

# Detailed Outline
{detailed_outline}
"""

        # 选择使用的大纲
        used_outline: str = outline
        if Writer.Config.EXPAND_OUTLINE:
            used_outline = mega_outline

        # 生成章节内容
        self.logger.Log("Starting Chapter Writing", 5)
        chapters = []
        total_word_count = 0
        for i in range(1, num_chapters + 1):
            self.logger.Log(f"正在生成第 {i}/{num_chapters} 章 (已生成 {total_word_count} 字)", 5)
            chapter = Writer.Chapter.ChapterGenerator.GenerateChapter(
                self.interface,
                self.logger,
                i,
                num_chapters,
                outline,
                chapters,
                Writer.Config.OUTLINE_QUALITY,
                base_context,
            )
            chapter = f"### Chapter {i}\n\n{chapter}"
            chapters.append(chapter)
            chapter_word_count = Writer.Statistics.GetWordCount(chapter)
            total_word_count += chapter_word_count
            self.logger.Log(f"第 {i} 章字数: {chapter_word_count}, 总字数: {total_word_count}", 2)

            # 更新并保存故事信息
            self.story_info.update({f"Chapter_{i}": chapter})
            Writer.Utils.FileHandler.FileHandler.save_temp_story_info(self.title, self.story_info)

        # 编辑整个故事
        story_body_text: str = ""

        if Writer.Config.ENABLE_FINAL_EDIT_PASS:
            chapters = Writer.NovelEditor.EditNovel(
                self.interface, self.logger, chapters, outline, num_chapters
            )
        self.story_info.update({"UnscrubbedChapters": chapters})
        Writer.Utils.FileHandler.FileHandler.save_temp_story_info(self.title, self.story_info)

        # 清理故事内容
        if not Writer.Config.SCRUB_NO_SCRUB:
            chapters = Writer.Scrubber.ScrubNovel(
                self.interface, self.logger, chapters, num_chapters
            )
        else:
            self.logger.Log(f"Skipping Scrubbing Due To Config", 4)
        self.story_info.update({"ScrubbedChapter": chapters})
        Writer.Utils.FileHandler.FileHandler.save_temp_story_info(self.title, self.story_info)

        # 如果需要翻译故事
        if Writer.Config.TRANSLATE_LANGUAGE != "":
            chapters = Writer.Translator.TranslateNovel(
                self.interface, self.logger, chapters, num_chapters, Writer.Config.TRANSLATE_LANGUAGE
            )
        else:
            self.logger.Log(f"No Novel Translation Requested, Skipping Translation Step", 4)
        self.story_info.update({"TranslatedChapters": chapters})
        Writer.Utils.FileHandler.FileHandler.save_temp_story_info(self.title, self.story_info)

        # 编译故事文本
        for chapter in chapters:
            story_body_text += chapter + "\n\n\n"

        return story_body_text, self.story_info

    def get_elapsed_time(self) -> float:
        """获取故事生成耗时"""
        return time.time() - self.start_time 