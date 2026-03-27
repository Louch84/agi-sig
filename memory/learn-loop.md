# Self-Learning Loop

## How I Learn

### Trigger Sources
- I try something and it fails
- Louch asks for something I can't do
- I notice a gap in my capabilities
- Web research reveals something I should know
- I have an idea for improvement

### Learning Steps
1. **Log the gap** → add to gaps.md
2. **Research** → web search, docs, experimentation
3. **Build** → create skill, write code, or update memory
4. **Test** → run it, verify it works
5. **Document** → update gaps.md + memory with what I learned
6. **Commit** → push to git if meaningful

### Self-Evaluation (Weekly)
- Review gaps.md
- Ask: what did I learn this week?
- What still sucks?
- What's the next priority?

## Skill Creation Workflow
1. Run: `init_skill.py <name> --path skills/`
2. Write SKILL.md + resources
3. Test
4. Package: `package_skill.py <path>`
5. Update memory/gaps.md

## Code Execution
- Use `exec` for one-off code
- Results persist in session only
- For persistent code: write to workspace files
