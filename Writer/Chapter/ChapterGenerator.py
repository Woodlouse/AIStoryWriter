import json
from typing import List, Tuple, Optional
from dataclasses import dataclass

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts
import Writer.Scene.ChapterByScene

@dataclass
class ChapterContext:
    chapter_num: int
    total_chapters: int
    outline: str
    previous_chapters: List[str]
    quality_threshold: int
    base_context: str
    
class ChapterGenerator:
    def __init__(self, interface, logger):
        self.interface = interface
        self.logger = logger
        
    def _create_base_message_history(self, ctx: ChapterContext) -> List[dict]:
        """创建基础消息历史"""
        self.logger.Log(f"Creating Base Langchain For Chapter {ctx.chapter_num} Generation", 2)
        
        message_history = [
            self.interface.BuildSystemQuery(
                Writer.Prompts.CHAPTER_GENERATION_INTRO.format(
                    _ChapterNum=ctx.chapter_num, 
                    _TotalChapters=ctx.total_chapters
                )
            )
        ]
        return message_history

    def _get_context_history(self, ctx: ChapterContext) -> str:
        """获取上下文历史"""
        if not ctx.previous_chapters:
            return ""
            
        chapter_superlist = "\n".join(ctx.previous_chapters)
        return Writer.Prompts.CHAPTER_HISTORY_INSERT.format(
            _Outline=ctx.outline, 
            ChapterSuperlist=chapter_superlist
        )

    def _extract_chapter_outline(self, ctx: ChapterContext) -> str:
        """提取特定章节大纲"""
        self.logger.Log("Extracting Chapter Specific Outline", 4)
        
        messages = [
            self.interface.BuildSystemQuery(Writer.Prompts.CHAPTER_GENERATION_INTRO),
            self.interface.BuildUserQuery(
                Writer.Prompts.CHAPTER_GENERATION_PROMPT.format(
                    _Outline=ctx.outline, 
                    _ChapterNum=ctx.chapter_num
                )
            )
        ]
        
        messages = self.interface.SafeGenerateText(
            self.logger,
            messages,
            Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
            _MinWordCount=120
        )
        
        self.logger.Log("Created Chapter Specific Outline", 4)
        return self.interface.GetLastMessageText(messages)

    def _get_last_chapter_summary(self, ctx: ChapterContext) -> str:
        """获取上一章节摘要"""
        if not ctx.previous_chapters:
            return ""
            
        self.logger.Log("Creating Summary Of Last Chapter Info", 3)
        messages = [
            self.interface.BuildSystemQuery(Writer.Prompts.CHAPTER_SUMMARY_INTRO),
            self.interface.BuildUserQuery(
                Writer.Prompts.CHAPTER_SUMMARY_PROMPT.format(
                    _ChapterNum=ctx.chapter_num,
                    _TotalChapters=ctx.total_chapters,
                    _Outline=ctx.outline,
                    _LastChapter=ctx.previous_chapters[-1]
                )
            )
        ]
        
        messages = self.interface.SafeGenerateText(
            self.logger,
            messages,
            Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
            _MinWordCount=100
        )
        
        self.logger.Log("Created Summary Of Last Chapter Info", 3)
        return self.interface.GetLastMessageText(messages)

    def _generate_stage(
        self,
        stage_name: str,
        stage_prompt: str,
        model: str,
        ctx: ChapterContext,
        context_history: str,
        last_chapter_summary: str,
        chapter_outline: str,
        previous_stage_content: str = "",
        base_messages: List[dict] = None,
        stage_number: int = 1
    ) -> str:
        """生成单个阶段的内容"""
        iter_counter = 0
        feedback = ""
        
        while True:
            # 根据阶段号设置正确的内容
            stage1_content = previous_stage_content if stage_number == 2 else ""
            stage2_content = previous_stage_content if stage_number == 3 else ""
            
            prompt = stage_prompt.format(
                ContextHistoryInsert=context_history,
                _ChapterNum=ctx.chapter_num,
                _TotalChapters=ctx.total_chapters,
                ThisChapterOutline=chapter_outline,
                FormattedLastChapterSummary=last_chapter_summary,
                Feedback=feedback,
                _BaseContext=ctx.base_context,
                Stage1Chapter=stage1_content,
                Stage2Chapter=stage2_content
            )

            self.logger.Log(
                f"Generating Chapter ({stage_name}) {ctx.chapter_num}/{ctx.total_chapters} (第 {iter_counter + 1} 次尝试)",
                5
            )
            
            messages = (base_messages or []).copy()
            messages.append(self.interface.BuildUserQuery(prompt))
            
            messages = self.interface.SafeGenerateText(
                self.logger,
                messages,
                model,
                _SeedOverride=iter_counter + Writer.Config.SEED,
                _MinWordCount=100
            )
            
            stage_content = self.interface.GetLastMessageText(messages)
            iter_counter += 1

            if iter_counter > Writer.Config.CHAPTER_MAX_REVISIONS:
                self.logger.Log(f"章节生成似乎卡住了 - 已尝试 {iter_counter} 次，强制退出", 7)
                break
                
            result, feedback = Writer.Chapter.ChapterGenSummaryCheck.LLMSummaryCheck(
                self.interface, 
                self.logger, 
                chapter_outline, 
                stage_content
            )
            
            if result:
                self.logger.Log(f"Done Generating Chapter ({stage_name})", 5)
                break
                
        return stage_content

    def _revise_chapter(
        self, 
        chapter: str,
        ctx: ChapterContext,
        base_messages: List[dict]
    ) -> str:
        """修改章节内容"""
        if Writer.Config.CHAPTER_NO_REVISIONS:
            self.logger.Log("Chapter Revision Disabled In Config", 5)
            return chapter

        self.logger.Log(f"Starting Revision Loop For Chapter {ctx.chapter_num}", 4)
        
        writing_history = base_messages.copy()
        iterations = 0
        
        while True:
            iterations += 1
            feedback = Writer.LLMEditor.GetFeedbackOnChapter(
                self.interface, 
                self.logger, 
                chapter, 
                ctx.outline
            )
            rating = Writer.LLMEditor.GetChapterRating(
                self.interface, 
                self.logger, 
                chapter
            )

            if iterations > Writer.Config.CHAPTER_MAX_REVISIONS:
                self.logger.Log(f"Maximum revision count reached: {Writer.Config.CHAPTER_MAX_REVISIONS}", 4)
                break
                
            if (iterations > Writer.Config.CHAPTER_MIN_REVISIONS and 
                rating >= ctx.quality_threshold):
                self.logger.Log(f"Quality threshold met (Rating: {rating}, Required: {ctx.quality_threshold})", 4)
                break

            chapter, writing_history = self._apply_revision(
                chapter, 
                feedback, 
                writing_history
            )

        return chapter

    def _apply_revision(
        self, 
        chapter: str, 
        feedback: str, 
        history: List[dict]
    ) -> Tuple[str, List[dict]]:
        """应用单次修改"""
        self.logger.Log("Applying Chapter Revision", 5)
        
        revision_prompt = Writer.Prompts.CHAPTER_REVISION.format(
            _Chapter=chapter, 
            _Feedback=feedback
        )
        
        messages = history.copy()
        messages.append(self.interface.BuildUserQuery(revision_prompt))
        
        messages = self.interface.SafeGenerateText(
            self.logger,
            messages,
            Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
            _MinWordCount=100
        )
        
        revised_chapter = self.interface.GetLastMessageText(messages)
        self.logger.Log("Completed Chapter Revision", 5)
        
        return revised_chapter, messages

    def generate_chapter(
        self,
        chapter_num: int,
        total_chapters: int,
        outline: str,
        previous_chapters: List[str] = None,
        quality_threshold: int = 85,
        base_context: str = ""
    ) -> str:
        """生成完整的章节内容"""
        ctx = ChapterContext(
            chapter_num=chapter_num,
            total_chapters=total_chapters,
            outline=outline,
            previous_chapters=previous_chapters or [],
            quality_threshold=quality_threshold,
            base_context=base_context
        )
        
        # 初始化基础消息历史
        base_messages = self._create_base_message_history(ctx)
        context_history = self._get_context_history(ctx)
        
        # 获取章节大纲和上一章摘要
        chapter_outline = self._extract_chapter_outline(ctx)
        last_chapter_summary = self._get_last_chapter_summary(ctx)
        
        # 生成初始情节
        if not Writer.Config.SCENE_GENERATION_PIPELINE:
            stage1_content = self._generate_stage(
                "Plot",
                Writer.Prompts.CHAPTER_GENERATION_STAGE1,
                Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
                ctx,
                context_history,
                last_chapter_summary,
                chapter_outline,
                base_messages=base_messages,
                stage_number=1
            )
        else:
            stage1_content = Writer.Scene.ChapterByScene.ChapterByScene(
                self.interface,
                self.logger,
                chapter_outline,
                outline,
                base_context
            )
            
        # 添加角色发展
        stage2_content = self._generate_stage(
            "Character Development",
            Writer.Prompts.CHAPTER_GENERATION_STAGE2,
            Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
            ctx,
            context_history,
            last_chapter_summary,
            chapter_outline,
            stage1_content,
            base_messages,
            stage_number=2
        )
        
        # 添加对话
        stage3_content = self._generate_stage(
            "Dialogue",
            Writer.Prompts.CHAPTER_GENERATION_STAGE3,
            Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
            ctx,
            context_history,
            last_chapter_summary,
            chapter_outline,
            stage2_content,
            base_messages,
            stage_number=3
        )
        
        # 修改和完善
        final_chapter = self._revise_chapter(
            stage3_content,
            ctx,
            base_messages
        )
        
        return final_chapter

# 为了保持向后兼容性的函数
def GenerateChapter(
    Interface,
    _Logger,
    _ChapterNum: int,
    _TotalChapters: int,
    _Outline: str,
    _Chapters: list = [],
    _QualityThreshold: int = 85,
    _BaseContext: str = ""
) -> str:
    """保持向后兼容的包装函数"""
    generator = ChapterGenerator(Interface, _Logger)
    return generator.generate_chapter(
        chapter_num=_ChapterNum,
        total_chapters=_TotalChapters,
        outline=_Outline,
        previous_chapters=_Chapters,
        quality_threshold=_QualityThreshold,
        base_context=_BaseContext
    )
