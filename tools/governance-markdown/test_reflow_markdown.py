import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from reflow_markdown import iter_markdown, project_root_paths, reflow_text


class ReflowMarkdownTests(unittest.TestCase):
    def test_joins_chinese_and_english_without_losing_word_boundaries(self):
        result = reflow_text(
            "本文件不等同于\nCodex Plan（计划模式）。任务开始时不读取。\n"
        )
        self.assertEqual(
            "本文件不等同于 Codex Plan（计划模式）。任务开始时不读取。\n",
            result.text + "\n",
        )
        self.assertEqual(1, result.joins)

    def test_joins_list_continuation_but_keeps_nested_list(self):
        result = reflow_text(
            "- 第一项内容继续\n  这是第一项的续行。\n  - 嵌套项目\n- 第二项。\n"
        )
        self.assertIn("- 第一项内容继续这是第一项的续行。", result.text)
        self.assertIn("  - 嵌套项目", result.text)
        self.assertEqual(1, result.joins)

        lazy = reflow_text("- A list item continues\nwithout indentation.\n")
        self.assertEqual("- A list item continues without indentation.", lazy.text)
        self.assertEqual(1, lazy.joins)

    def test_preserves_frontmatter_code_math_table_and_explicit_break(self):
        source = (
            "---\n"
            "title: test\n"
            "---\n"
            "普通段落第一行\n普通段落第二行。\n\n"
            "```text\n"
            "代码第一行\n代码第二行\n"
            "```\n\n"
            "\\[\n"
            "x = 1\n"
            "\\]\n\n"
            "| A | B |\n| --- | --- |\n| 1 | 2 |\n\n"
            "<!-- comment\n"
            "comment continuation\n"
            "-->\n\n"
            "显式换行  \n下一行。\n"
        )
        result = reflow_text(source)
        self.assertIn("普通段落第一行普通段落第二行。", result.text)
        self.assertIn("代码第一行\n代码第二行", result.text)
        self.assertIn("\\[\nx = 1\n\\]", result.text)
        self.assertIn("| A | B |\n| --- | --- |", result.text)
        self.assertIn("<!-- comment\ncomment continuation\n-->", result.text)
        self.assertIn("显式换行  \n下一行。", result.text)
        self.assertEqual(1, result.joins)

    def test_project_root_probe_reaches_current_nested_docs_but_not_history(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs" / "治理日志").mkdir(parents=True)
            (root / "docs" / "历史").mkdir()
            (root / "AGENTS.md").write_text("# Entry\n", encoding="utf-8")
            current = root / "docs" / "治理日志" / "2026-08.md"
            current.write_text("当前段落第一行\n当前段落第二行。\n", encoding="utf-8")
            historical = root / "docs" / "历史" / "2026-07.md"
            historical.write_text("历史段落第一行\n历史段落第二行。\n", encoding="utf-8")

            selected = set(iter_markdown(project_root_paths(root)))

            self.assertIn((root / "AGENTS.md").resolve(), selected)
            self.assertIn(current.resolve(), selected)
            self.assertNotIn(historical.resolve(), selected)


if __name__ == "__main__":
    unittest.main()
