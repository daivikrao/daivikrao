<div align="center">

<img src="https://raw.githubusercontent.com/daivikrao/daivikrao/main/assets/status.svg?v=0-init" width="100%" alt="systemctl status daivik.service — Daivik, CS grad student at Texas A&M, ex-Software Engineer at Fidelity Investments"/>

<a href="https://github.com/daivikrao/daivikrao/issues/new?title=ping&body=%F0%9F%91%8B%20Just%20hit%20**Create**%20%E2%80%94%20a%20GitHub%20Action%20takes%20it%20from%20here."><img src="https://img.shields.io/badge/ping-daivik.service-3fb950?style=for-the-badge&logo=githubactions&logoColor=white&labelColor=161b22" alt="Ping daivik.service"/></a>

<sub>Click the button, then hit <b>Create</b>. A GitHub Action logs your ping in the terminal above and replies to you within a minute.</sub>

</div>

---

### 🛠️ Tech Stack

<p align="left">
  <img src="https://skillicons.dev/icons?i=python,java,cpp,js,react,html,css,php,mysql,git,github,linux,vscode&perline=13" />
</p>

---

### 📊 GitHub Stats

<div align="center">
  <img height="165" src="https://github-readme-stats.vercel.app/api?username=daivikrao&show_icons=true&theme=tokyonight&hide_border=true&count_private=true" />
  <img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=daivikrao&layout=compact&theme=tokyonight&hide_border=true&langs_count=6" />
</div>

<div align="center">
  <img src="https://streak-stats.demolab.com?user=daivikrao&theme=tokyonight&hide_border=true" />
</div>

<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=daivikrao&theme=tokyo-night&hide_border=true&area=true" width="100%"/>
</div>

---

<details>
<summary><b>⚙️ How the ping works</b></summary>
<br/>

Every ping is a tiny event-driven pipeline, built entirely on GitHub:

```mermaid
flowchart LR
    A["👋 You open an issue<br/>titled 'ping'"] --> B["⚡ GitHub Action<br/>(issues: opened)"]
    B --> C["🐍 ping.py record<br/>dedupes + logs to pings.json"]
    C --> D["🎨 ping.py render<br/>re-draws status.svg"]
    D --> E["📦 commit + push<br/>busts image cache"]
    E --> F["💬 replies 200 OK<br/>and closes the issue"]
```

- **Rate limiting:** pinging again within 30 minutes gets a friendly `429` instead of a duplicate log entry.
- **Safe by design:** only your GitHub username is shown, never free text from the issue.
- **Concurrency:** runs are serialized so simultaneous pings never clobber each other.

Source: [`ping.yml`](.github/workflows/ping.yml) · [`ping.py`](scripts/ping.py)

</details>
