import datetime
import Writer.Config

class Statistics:
    @staticmethod
    def get_word_count(text: str) -> int:
        """计算文本中的单词数"""
        return len(text.split())

    @staticmethod
    def format_stats(total_words: int, elapsed_time: float, title: str, summary: str, 
                    tags: str, score: str, base_prompt: str) -> str:
        """格式化统计信息为字符串"""
        stats = "Work Statistics:  \n"
        stats += f" - Total Words: {total_words}  \n"
        stats += f" - Title: {title}  \n"
        stats += f" - Summary: {summary}  \n"
        stats += f" - Tags: {tags}  \n"
        stats += f" - Score: {score}  \n"
        stats += f" - Generation Start Date: {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}  \n"
        stats += f" - Generation Total Time: {elapsed_time}s  \n"
        stats += f" - Generation Average WPM: {60 * (total_words/elapsed_time)}  \n"

        stats += "\n\nUser Settings:  \n"
        stats += f" - Base Prompt: {base_prompt}  \n"

        stats += "\n\nGeneration Settings:  \n"
        stats += f" - Generator: AIStoryGenerator_2024-06-27  \n"
        stats += f" - Base Outline Writer Model: {Writer.Config.INITIAL_OUTLINE_WRITER_MODEL}  \n"
        stats += f" - Chapter Outline Writer Model: {Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL}  \n"
        stats += f" - Chapter Writer (Stage 1: Plot) Model: {Writer.Config.CHAPTER_STAGE1_WRITER_MODEL}  \n"
        stats += f" - Chapter Writer (Stage 2: Char Development) Model: {Writer.Config.CHAPTER_STAGE2_WRITER_MODEL}  \n"
        stats += f" - Chapter Writer (Stage 3: Dialogue) Model: {Writer.Config.CHAPTER_STAGE3_WRITER_MODEL}  \n"
        stats += f" - Chapter Writer (Stage 4: Final Pass) Model: {Writer.Config.CHAPTER_STAGE4_WRITER_MODEL}  \n"
        stats += f" - Chapter Writer (Revision) Model: {Writer.Config.CHAPTER_REVISION_WRITER_MODEL}  \n"
        stats += f" - Revision Model: {Writer.Config.REVISION_MODEL}  \n"
        stats += f" - Eval Model: {Writer.Config.EVAL_MODEL}  \n"
        stats += f" - Info Model: {Writer.Config.INFO_MODEL}  \n"
        stats += f" - Scrub Model: {Writer.Config.SCRUB_MODEL}  \n"
        stats += f" - Seed: {Writer.Config.SEED}  \n"
        stats += f" - Outline Min Revisions: {Writer.Config.OUTLINE_MIN_REVISIONS}  \n"
        stats += f" - Outline Max Revisions: {Writer.Config.OUTLINE_MAX_REVISIONS}  \n"
        stats += f" - Chapter Min Revisions: {Writer.Config.CHAPTER_MIN_REVISIONS}  \n"
        stats += f" - Chapter Max Revisions: {Writer.Config.CHAPTER_MAX_REVISIONS}  \n"
        stats += f" - Chapter Disable Revisions: {Writer.Config.CHAPTER_NO_REVISIONS}  \n"
        stats += f" - Disable Scrubbing: {Writer.Config.SCRUB_NO_SCRUB}  \n"

        return stats 