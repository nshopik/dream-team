# Shared references live in non-user-invocable skills, loaded by name

A reference two or more skills follow lives in its own skill with `user-invocable: false`
(`doc-conventions`, `local-tracker`), and callers load it through the Skill tool by name; a
section of another skill is cited as `dream-team:<skill>` and its section name. No skill or agent
reaches into another skill's folder with a `<base directory>/../<skill>/` path or a `../<skill>/`
link, and `test_skill_links.py` fails on one. Paths into another skill broke silently when
`7d6c78a` moved the shared references: installed 26.11.2 still pointed at `../../references/`
and a brainstorm session loaded a file that no longer existed; a skill name survives a file
move, a path into an owner skill's folder does not.
