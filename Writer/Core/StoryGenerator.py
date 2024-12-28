import time
from typing import List, Dict, Tuple

import Writer.Config
import Writer.Interface.Wrapper
import Writer.PrintUtils
import Writer.Chapter.ChapterDetector
import Writer.Scrubber
import Writer.Statistics
import Writer.OutlineGenerator
import Writer.Chapter.ChapterGenerator
import Writer.StoryInfo
import Writer.NovelEditor
import Writer.Translator

class StoryGenerator:
    def __init__(self, interface: Writer.Interface.Wrapper.Interface, logger: Writer.PrintUtils.Logger):
        self.interface = interface
        self.logger = logger
        self.start_time = time.time()

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
        base_prompt = prompt

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
                chapter_outline, messages = Writer.OutlineGenerator.GeneratePerChapterOutline(
                    self.interface, self.logger, chapter, outline, messages
                )
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
        for i in range(1, num_chapters + 1):
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
            self.logger.Log(f"Chapter Word Count: {chapter_word_count}", 2)

        # 编辑整个故事
        story_body_text: str = ""
        story_info_json: Dict = {
            "Outline": outline,
            "StoryElements": elements,
            "RoughChapterOutline": rough_chapter_outline,
            "BaseContext": base_context
        }

        if Writer.Config.ENABLE_FINAL_EDIT_PASS:
            chapters = Writer.NovelEditor.EditNovel(
                self.interface, self.logger, chapters, outline, num_chapters
            )
        story_info_json.update({"UnscrubbedChapters": chapters})

        # 清理故事内容
        if not Writer.Config.SCRUB_NO_SCRUB:
            chapters = Writer.Scrubber.ScrubNovel(
                self.interface, self.logger, chapters, num_chapters
            )
        else:
            self.logger.Log(f"Skipping Scrubbing Due To Config", 4)
        story_info_json.update({"ScrubbedChapter": chapters})

        # 如果需要翻译故事
        if Writer.Config.TRANSLATE_LANGUAGE != "":
            chapters = Writer.Translator.TranslateNovel(
                self.interface, self.logger, chapters, num_chapters, Writer.Config.TRANSLATE_LANGUAGE
            )
        else:
            self.logger.Log(f"No Novel Translation Requested, Skipping Translation Step", 4)
        story_info_json.update({"TranslatedChapters": chapters})

        # 编译故事文本
        for chapter in chapters:
            story_body_text += chapter + "\n\n\n"

        # 生成故事信息
        messages = []
        messages.append(self.interface.BuildUserQuery(outline))
        info = Writer.StoryInfo.GetStoryInfo(self.interface, self.logger, messages)
        story_info_json.update({
            "Title": info["标题"],
            "Summary": info["摘要"],
            "Tags": info["标签"],
            "Score": info["整体评分"]
        })

        return story_body_text, story_info_json

    def get_elapsed_time(self) -> float:
        """获取故事生成耗时"""
        return time.time() - self.start_time 