#!/bin/python3

from Writer.CLI.ArgumentParser import ArgumentParser
from Writer.Core.StoryGenerator import StoryGenerator
from Writer.Utils.FileHandler import FileHandler
from Writer.Utils.Statistics import Statistics
import Writer.Interface.Wrapper
import Writer.PrintUtils

def generate_one_story(interface, sys_logger, prompt):
    """生成一个故事"""
    # 初始化故事生成器
    story_generator = StoryGenerator(interface, sys_logger)

    # 生成故事
    story_body_text, story_info_json = story_generator.generate(prompt)

    # 获取故事信息
    title = story_info_json["Title"]
    summary = story_info_json["Summary"]
    tags = story_info_json["Tags"]
    score = story_info_json["Score"]

    # 打印基本信息
    print("---------------------------------------------")
    print(f"Story Title: {title}")
    print(f"Summary: {summary}")
    print(f"Tags: {tags}")
    print(f"Score: {score}")
    print("---------------------------------------------")

    # 计算统计信息
    elapsed_time = story_generator.get_elapsed_time()
    total_words = Statistics.get_word_count(story_body_text)
    sys_logger.Log(f"Story Total Word Count: {total_words}", 4)

    # 格式化统计信息
    stats = Statistics.format_stats(
        total_words=total_words,
        elapsed_time=elapsed_time,
        title=title,
        summary=summary,
        tags=tags,
        score=score,
        base_prompt=prompt
    )

    # 保存故事
    FileHandler.save_story(
        title=title,
        story_body=story_body_text,
        stats=stats,
        outline=story_info_json["Outline"],
        story_info=story_info_json
    )

def main():
    # 解析命令行参数
    args = ArgumentParser.parse_args()
    ArgumentParser.update_config(args)

    # 获取使用的模型列表
    models = [
        args.InitialOutlineModel,
        args.ChapterOutlineModel,
        args.ChapterS1Model,
        args.ChapterS2Model,
        args.ChapterS3Model,
        args.ChapterS4Model,
        args.ChapterRevisionModel,
        args.EvalModel,
        args.RevisionModel,
        args.InfoModel,
        args.ScrubModel,
        args.CheckerModel,
        args.TranslatorModel,
    ]
    models = list(set(models))

    # 初始化日志记录器
    sys_logger = Writer.PrintUtils.Logger()

    # 初始化接口
    sys_logger.Log("Created OLLAMA Interface", 5)
    interface = Writer.Interface.Wrapper.Interface(models)

    # 加载用户提示
    prompt = FileHandler.load_prompt(args.Prompt)

    # 根据指定次数生成故事
    for i in range(args.Times):
        print(f"\n=== 正在生成第 {i+1}/{args.Times} 个故事 ===\n")
        generate_one_story(interface, sys_logger, prompt)

if __name__ == "__main__":
    main()