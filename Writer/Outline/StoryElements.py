import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config


def GenerateStoryElements(Interface, _Logger, _OutlinePrompt):

    Prompt: str = f"""
我正在写一个虚构的故事，希望你能帮我写出故事的基本要素。

这是我的故事提示:
<PROMPT>
{_OutlinePrompt}
</PROMPT>

请按以下格式回复:

<RESPONSE_TEMPLATE>
# 故事标题

## 体裁
- **类别**: (例如：言情、悬疑、科幻、奇幻、恐怖)

## 主题
- **核心思想或寓意**:

## 节奏
- **速度**: (例如：缓慢、快速)

## 风格
- **语言运用**: (例如：句式结构、词汇、语气、修辞手法)

## 情节
- **开端**:
- **发展**:
- **高潮**:
- **转折**:
- **结局**:

## 场景
### 场景1
- **时间**: (例如：现代、未来、过去)
- **地点**: (例如：城市、乡村、另一个星球)
- **文化**: (例如：现代、中世纪、外星)
- **氛围**: (例如：阴郁、高科技、反乌托邦)

(可按上述结构添加更多场景)

## 冲突
- **类型**: (例如：内心冲突、外部冲突)
- **描述**:

## 象征
### 象征1
- **符号**:
- **含义**:

(可按上述结构添加更多象征)

## 人物
### 主要人物
#### 主角1
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **动机**:

(可按上述结构添加更多主要人物)


### 配角
#### 人物1
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

#### 人物2
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

#### 人物3
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

#### 人物4
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

#### 人物5
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

#### 人物6
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

#### 人物7
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

#### 人物8
- **姓名**:
- **外貌描述**:
- **性格**:
- **背景**:
- **在故事中的作用**:

(可按上述结构添加更多配角)

</RESPONSE_TEMPLATE>

当然，不要包含XML标签 - 这些只是用来表示示例。
另外，括号中的内容只是为了让你更好地理解要写什么，在回复中也应该省略。
    
    """

    # Generate Initial Story Elements
    _Logger.Log(f"Generating Main Story Elements", 4)
    Messages = [Interface.BuildUserQuery(Prompt)]
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=150
    )
    Elements: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Generating Main Story Elements", 4)

    return Elements
