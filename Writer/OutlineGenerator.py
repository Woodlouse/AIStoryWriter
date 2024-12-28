import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Outline.StoryElements
import Writer.Prompts
from typing import Tuple, Dict, Optional


def _extract_base_context(Interface, _Logger, _OutlinePrompt: str) -> str:
    """提取基础上下文信息"""
    _Logger.Log("Extracting Important Base Context", 4)
    prompt = Writer.Prompts.GET_IMPORTANT_BASE_PROMPT_INFO.format(_Prompt=_OutlinePrompt)
    messages = [Interface.BuildUserQuery(prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL
    )
    base_context = Interface.GetLastMessageText(messages)
    _Logger.Log("Done Extracting Important Base Context", 4)
    return base_context


def _generate_initial_outline(Interface, _Logger, _OutlinePrompt: str, story_elements: str) -> str:
    """生成初始大纲"""
    _Logger.Log("Generating Initial Outline", 4)
    prompt = Writer.Prompts.INITIAL_OUTLINE_PROMPT.format(
        StoryElements=story_elements, _OutlinePrompt=_OutlinePrompt
    )
    messages = [Interface.BuildUserQuery(prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=250
    )
    outline = Interface.GetLastMessageText(messages)
    _Logger.Log("Done Generating Initial Outline", 4)
    return outline


def _revise_outline_with_feedback(Interface, _Logger, outline: str, iterations: int = 0) -> Tuple[str, bool]:
    """根据反馈修改大纲"""
    try:
        feedback = Writer.LLMEditor.GetFeedbackOnOutline(Interface, _Logger, outline)
        meets_standards = Writer.LLMEditor.GetOutlineRating(Interface, _Logger, outline)
        
        if iterations >= Writer.Config.OUTLINE_MAX_REVISIONS:
            _Logger.Log("Reached maximum revision attempts", 3)
            return outline, meets_standards
            
        if iterations >= Writer.Config.OUTLINE_MIN_REVISIONS and meets_standards:
            _Logger.Log("Quality standards met", 4)
            return outline, meets_standards
            
        revised_outline, _ = ReviseOutline(Interface, _Logger, outline, feedback)
        return _revise_outline_with_feedback(Interface, _Logger, revised_outline, iterations + 1)
        
    except Exception as e:
        _Logger.Log(f"Error in outline revision: {str(e)}", 7)
        return outline, False


def GenerateOutline(Interface, _Logger, _OutlinePrompt: str, _QualityThreshold: int = 85) -> Tuple[str, str, str, str]:
    """生成故事大纲的主函数"""
    try:
        # 提取基础上下文
        base_context = _extract_base_context(Interface, _Logger, _OutlinePrompt)
        
        # 生成故事元素
        story_elements = Writer.Outline.StoryElements.GenerateStoryElements(
            Interface, _Logger, _OutlinePrompt
        )
        
        # 生成初始大纲
        outline = _generate_initial_outline(Interface, _Logger, _OutlinePrompt, story_elements)
        
        # 进入反馈和修改循环
        _Logger.Log("Entering Feedback/Revision Loop", 3)
        final_outline, meets_standards = _revise_outline_with_feedback(Interface, _Logger, outline)
        
        if not meets_standards:
            _Logger.Log("Warning: Final outline may not meet all quality standards", 3)
        
        # 生成最终大纲
        complete_outline = f"""
{base_context}

{story_elements}

{final_outline}
        """
        
        return complete_outline, story_elements, final_outline, base_context
        
    except Exception as e:
        _Logger.Log(f"Critical error in outline generation: {str(e)}", 7)
        raise


def ReviseOutline(Interface, _Logger, _Outline: str, _Feedback: str, _History: list = None) -> Tuple[str, list]:
    """修改大纲的辅助函数"""
    if _History is None:
        _History = []
        
    try:
        revision_prompt = Writer.Prompts.OUTLINE_REVISION_PROMPT.format(
            _Outline=_Outline, _Feedback=_Feedback
        )

        _Logger.Log("Revising Outline", 2)
        messages = _History.copy()
        messages.append(Interface.BuildUserQuery(revision_prompt))
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=250
        )
        revised_text = Interface.GetLastMessageText(messages)
        _Logger.Log("Done Revising Outline", 2)

        return revised_text, messages
        
    except Exception as e:
        _Logger.Log(f"Error in outline revision: {str(e)}", 7)
        return _Outline, _History


def GeneratePerChapterOutline(Interface, _Logger, _Chapter: int, _Outline: str, _History: list = None) -> Tuple[str, list]:
    """生成每章大纲的函数"""
    if _History is None:
        _History = []
        
    try:
        revision_prompt = Writer.Prompts.CHAPTER_OUTLINE_PROMPT.format(
            _Chapter=_Chapter,
            _Outline=_Outline
        )
        _Logger.Log(f"Generating Outline For Chapter {_Chapter}", 5)
        messages = _History.copy()
        messages.append(Interface.BuildUserQuery(revision_prompt))
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, _MinWordCount=50
        )
        chapter_outline = Interface.GetLastMessageText(messages)
        _Logger.Log(f"Done Generating Outline For Chapter {_Chapter}", 5)

        return chapter_outline, messages
        
    except Exception as e:
        _Logger.Log(f"Error generating chapter outline: {str(e)}", 7)
        return "", _History
