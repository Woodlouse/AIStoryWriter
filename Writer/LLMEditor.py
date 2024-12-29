import Writer.PrintUtils
import Writer.Prompts

import json


def GetFeedbackOnOutline(Interface, _Logger, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.CRITIC_OUTLINE_INTRO))

    StartingPrompt: str = Writer.Prompts.CRITIC_OUTLINE_PROMPT.format(_Outline=_Outline)

    _Logger.Log("Prompting LLM To Critique Outline", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL, _MinWordCount=70
    )
    _Logger.Log("Finished Getting Outline Feedback", 5)

    return Interface.GetLastMessageText(History)


def GetOutlineRating(
    Interface,
    _Logger,
    _Outline: str,
):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.OUTLINE_COMPLETE_INTRO))

    StartingPrompt: str = Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(
        _Outline=_Outline
    )

    _Logger.Log("正在请求 LLM 评估大纲质量...", 5)

    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.EVAL_MODEL, _Format="json"
    )
    _Logger.Log("已收到大纲评估结果", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"大纲评估结果: {Rating} (经过 {Iters} 次尝试)", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log(f"JSON 解析失败，已达到最大重试次数 (5次)", 7)
                return False
            _Logger.Log(f"第 {Iters} 次解析 JSON 失败: {str(E)}, 正在重试...", 7)
            EditPrompt: str = Writer.Prompts.JSON_PARSE_ERROR.format(_Error=E)
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("请求 LLM 修正 JSON 格式", 7)
            History = Interface.SafeGenerateText(
                _Logger, History, Writer.Config.EVAL_MODEL, _Format="json"
            )
            _Logger.Log("已收到修正后的 JSON", 6)


def GetFeedbackOnChapter(Interface, _Logger, _Chapter: str, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(
        Interface.BuildSystemQuery(
            Writer.Prompts.CRITIC_CHAPTER_INTRO.format(_Chapter=_Chapter)
        )
    )

    # Disabled seeing the outline too.
    StartingPrompt: str = Writer.Prompts.CRITIC_CHAPTER_PROMPT.format(
        _Chapter=_Chapter, _Outline=_Outline
    )

    _Logger.Log("Prompting LLM To Critique Chapter", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL
    )
    _Logger.Log("Finished Getting Chapter Feedback", 5)

    return Interface.GetLastMessageText(Messages)


# Switch this to iscomplete true/false (similar to outline)
def GetChapterRating(Interface, _Logger, _Chapter: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_COMPLETE_INTRO))

    StartingPrompt: str = Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(
        _Chapter=_Chapter
    )

    _Logger.Log("正在请求 LLM 评估章节质量...", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.EVAL_MODEL
    )
    _Logger.Log("已收到章节评估结果", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            _Logger.Log(f"正在解析章节评估结果 (第 {Iters} 次尝试)", 5)
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"章节评估结果: {Rating} (经过 {Iters} 次尝试)", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log(f"JSON 解析失败，已达到最大重试次数 (5次)", 7)
                return False

            _Logger.Log(f"第 {Iters} 次解析 JSON 失败: {str(E)}, 正在重试...", 7)
            EditPrompt: str = Writer.Prompts.JSON_PARSE_ERROR.format(_Error=E)
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("请求 LLM 修正 JSON 格式", 7)
            History = Interface.SafeGenerateText(
                _Logger, History, Writer.Config.EVAL_MODEL
            )
            _Logger.Log("已收到修正后的 JSON", 6)
