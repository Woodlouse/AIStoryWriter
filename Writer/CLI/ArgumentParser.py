import argparse
import Writer.Config

class ArgumentParser:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("-Prompt", help="Path to file containing the prompt")
        parser.add_argument(
            "-Output",
            default="",
            type=str,
            help="Optional file output path, if none is speciifed, we will autogenerate a file name based on the story title",
        )
        parser.add_argument(
            "-InitialOutlineModel",
            default=Writer.Config.INITIAL_OUTLINE_WRITER_MODEL,
            type=str,
            help="Model to use for writing the base outline content",
        )
        parser.add_argument(
            "-ChapterOutlineModel",
            default=Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL,
            type=str,
            help="Model to use for writing the per-chapter outline content",
        )
        parser.add_argument(
            "-ChapterS1Model",
            default=Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
            type=str,
            help="Model to use for writing the chapter (stage 1: plot)",
        )
        parser.add_argument(
            "-ChapterS2Model",
            default=Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
            type=str,
            help="Model to use for writing the chapter (stage 2: character development)",
        )
        parser.add_argument(
            "-ChapterS3Model",
            default=Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
            type=str,
            help="Model to use for writing the chapter (stage 3: dialogue)",
        )
        parser.add_argument(
            "-ChapterS4Model",
            default=Writer.Config.CHAPTER_STAGE4_WRITER_MODEL,
            type=str,
            help="Model to use for writing the chapter (stage 4: final correction pass)",
        )
        parser.add_argument(
            "-ChapterRevisionModel",
            default=Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
            type=str,
            help="Model to use for revising the chapter until it meets criteria",
        )
        parser.add_argument(
            "-RevisionModel",
            default=Writer.Config.REVISION_MODEL,
            type=str,
            help="Model to use for generating constructive criticism",
        )
        parser.add_argument(
            "-EvalModel",
            default=Writer.Config.EVAL_MODEL,
            type=str,
            help="Model to use for evaluating the rating out of 100",
        )
        parser.add_argument(
            "-InfoModel",
            default=Writer.Config.INFO_MODEL,
            type=str,
            help="Model to use when generating summary/info at the end",
        )
        parser.add_argument(
            "-ScrubModel",
            default=Writer.Config.SCRUB_MODEL,
            type=str,
            help="Model to use when scrubbing the story at the end",
        )
        parser.add_argument(
            "-CheckerModel",
            default=Writer.Config.CHECKER_MODEL,
            type=str,
            help="Model to use when checking if the LLM cheated or not",
        )
        parser.add_argument(
            "-TranslatorModel",
            default=Writer.Config.TRANSLATOR_MODEL,
            type=str,
            help="Model to use if translation of the story is enabled",
        )
        parser.add_argument(
            "-Translate",
            default="",
            type=str,
            help="Specify a language to translate the story to - will not translate by default. Ex: 'French'",
        )
        parser.add_argument(
            "-TranslatePrompt",
            default="",
            type=str,
            help="Specify a language to translate your input prompt to. Ex: 'French'",
        )
        parser.add_argument("-Seed", default=12, type=int, help="Used to seed models.")
        parser.add_argument(
            "-OutlineMinRevisions",
            default=0,
            type=int,
            help="Number of minimum revisions that the outline must be given prior to proceeding",
        )
        parser.add_argument(
            "-OutlineMaxRevisions",
            default=3,
            type=int,
            help="Max number of revisions that the outline may have",
        )
        parser.add_argument(
            "-ChapterMinRevisions",
            default=0,
            type=int,
            help="Number of minimum revisions that the chapter must be given prior to proceeding",
        )
        parser.add_argument(
            "-ChapterMaxRevisions",
            default=3,
            type=int,
            help="Max number of revisions that the chapter may have",
        )
        parser.add_argument(
            "-NoChapterRevision", action="store_true", help="Disables Chapter Revisions"
        )
        parser.add_argument(
            "-NoScrubChapters",
            action="store_true",
            help="Disables a final pass over the story to remove prompt leftovers/outline tidbits",
        )
        parser.add_argument(
            "-ExpandOutline",
            action="store_true",
            default=True,
            help="Disables the system from expanding the outline for the story chapter by chapter prior to writing the story's chapter content",
        )
        parser.add_argument(
            "-EnableFinalEditPass",
            action="store_true",
            help="Enable a final edit pass of the whole story prior to scrubbing",
        )
        parser.add_argument(
            "-Debug",
            action="store_true",
            help="Print system prompts to stdout during generation",
        )
        parser.add_argument(
            "-SceneGenerationPipeline",
            action="store_true",
            default=True,
            help="Use the new scene-by-scene generation pipeline as an initial starting point for chapter writing",
        )
        parser.add_argument(
            "-Times",
            default=1,
            type=int,
            help="生成故事的次数，默认为1次",
        )
        
        return parser.parse_args()

    @staticmethod
    def update_config(args):
        Writer.Config.SEED = args.Seed
        Writer.Config.INITIAL_OUTLINE_WRITER_MODEL = args.InitialOutlineModel
        Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL = args.ChapterOutlineModel
        Writer.Config.CHAPTER_STAGE1_WRITER_MODEL = args.ChapterS1Model
        Writer.Config.CHAPTER_STAGE2_WRITER_MODEL = args.ChapterS2Model
        Writer.Config.CHAPTER_STAGE3_WRITER_MODEL = args.ChapterS3Model
        Writer.Config.CHAPTER_STAGE4_WRITER_MODEL = args.ChapterS4Model
        Writer.Config.CHAPTER_REVISION_WRITER_MODEL = args.ChapterRevisionModel
        Writer.Config.EVAL_MODEL = args.EvalModel
        Writer.Config.REVISION_MODEL = args.RevisionModel
        Writer.Config.INFO_MODEL = args.InfoModel
        Writer.Config.SCRUB_MODEL = args.ScrubModel
        Writer.Config.CHECKER_MODEL = args.CheckerModel
        Writer.Config.TRANSLATOR_MODEL = args.TranslatorModel
        Writer.Config.TRANSLATE_LANGUAGE = args.Translate
        Writer.Config.TRANSLATE_PROMPT_LANGUAGE = args.TranslatePrompt
        Writer.Config.OUTLINE_MIN_REVISIONS = args.OutlineMinRevisions
        Writer.Config.OUTLINE_MAX_REVISIONS = args.OutlineMaxRevisions
        Writer.Config.CHAPTER_MIN_REVISIONS = args.ChapterMinRevisions
        Writer.Config.CHAPTER_MAX_REVISIONS = args.ChapterMaxRevisions
        Writer.Config.CHAPTER_NO_REVISIONS = args.NoChapterRevision
        Writer.Config.SCRUB_NO_SCRUB = args.NoScrubChapters
        Writer.Config.EXPAND_OUTLINE = args.ExpandOutline
        Writer.Config.ENABLE_FINAL_EDIT_PASS = args.EnableFinalEditPass
        Writer.Config.OPTIONAL_OUTPUT_NAME = args.Output
        Writer.Config.SCENE_GENERATION_PIPELINE = args.SceneGenerationPipeline
        Writer.Config.DEBUG = args.Debug 