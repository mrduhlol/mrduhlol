from github import Github
import os

USERNAME = os.getenv("USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

g = Github(TOKEN)
user = g.get_user(USERNAME)

repos = list(user.get_repos())

repo_count = len(repos)
followers = user.followers

stars = 0
commits = 0
loc = 0

for repo in repos:
    try:
        stars += repo.stargazers_count

        commits += repo.get_commits().totalCount

        try:
            languages = repo.get_languages()
            loc += sum(languages.values())
        except:
            pass

    except:
        pass

template = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500">
<style>
text {{
    font-family: "JetBrains Mono", monospace;
    font-size: 20px;
    fill: #d6d6d6;
}}
.title {{
    fill: #ffffff;
    font-size: 26px;
}}
.orange {{
    fill: #f4a261;
}}
</style>

<rect width="100%" height="100%" rx="20" fill="#161b22"/>

<text x="40" y="50" class="title">{USERNAME}@github</text>

<text x="40" y="100" class="orange">OS:</text>
<text x="260" y="100">Windows 11, Linux</text>

<text x="40" y="140" class="orange">Role:</text>
<text x="260" y="140">AI Developer</text>

<text x="40" y="180" class="orange">IDE:</text>
<text x="260" y="180">VS Code</text>

<text x="40" y="240" class="orange">Repositories:</text>
<text x="360" y="240">{repo_count}</text>

<text x="40" y="280" class="orange">Stars:</text>
<text x="360" y="280">{stars}</text>

<text x="40" y="320" class="orange">Followers:</text>
<text x="360" y="320">{followers}</text>

<text x="40" y="360" class="orange">Commits:</text>
<text x="360" y="360">{commits}</text>

<text x="40" y="400" class="orange">Lines of Code:</text>
<text x="360" y="400">{loc:,}</text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/terminal.svg", "w", encoding="utf-8") as f:
    f.write(template)

print("Generated assets/terminal.svg")