import Writer.Config
import Writer.Prompts

import re
import json


def LLMCountChapters(Interface, _Logger, _Summary):

    Prompt = Writer.Prompts.CHAPTER_COUNT_PROMPT.format(_Summary=_Summary)

    _Logger.Log("正在请求 LLM 统计章节数量...", 5)
    Messages = []
    Messages.append(Interface.BuildUserQuery(Prompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.EVAL_MODEL, _Format="json"
    )
    _Logger.Log("已收到章节数量统计结果", 5)

    Iters: int = 0

    while True:

        RawResponse = Interface.GetLastMessageText(Messages)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            _Logger.Log(f"正在解析章节数量 (第 {Iters} 次尝试)", 5)
            TotalChapters = json.loads(RawResponse)["TotalChapters"]
            _Logger.Log(f"检测到总章节数: {TotalChapters} (经过 {Iters} 次尝试)", 5)
            return TotalChapters
        except Exception as E:
            if Iters > 4:
                _Logger.Log(f"JSON 解析失败，已达到最大重试次数 (5次)", 7)
                return -1
            _Logger.Log(f"第 {Iters} 次解析 JSON 失败: {str(E)}, 正在重试...", 7)
            EditPrompt: str = (
                f"请修正你的 JSON 格式。解析时遇到以下错误: {E}。请记住，你的响应会直接传入 JSON 解析器，所以不要包含任何额外的内容，只需要纯 JSON。"
            )
            Messages.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("请求 LLM 修正 JSON 格式", 7)
            Messages = Interface.SafeGenerateText(
                _Logger, Messages, Writer.Config.EVAL_MODEL, _Format="json"
            )
            _Logger.Log("已收到修正后的 JSON", 6)
