(() => {
  const el = (id) => document.getElementById(id);

  const defaultProject = (title = "Story Machine Modern") => ({
    title,
    dictionary: {
      verbs: ["LOOK", "HELP", "CHOOSE", "GO"],
      nouns: ["START"],
      articles: ["A", "AN", "THE"]
    },
    scenes: {
      START: {
        text: "You are at the beginning of your story.",
        choices: []
      }
    }
  });

  let project = defaultProject();
  let currentScene = "START";

  const status = (msg) => { el("status").textContent = msg; };
  const log = (msg) => { el("playLog").textContent += `${msg}\n`; };

  const normalize = (s) => (s || "").trim().toUpperCase();

  const addWord = (category, word) => {
    const w = normalize(word);
    if (!w) return;
    if (!project.dictionary[category]) return;
    if (!project.dictionary[category].includes(w)) project.dictionary[category].push(w);
  };

  const addScene = (sceneId, text) => {
    const id = normalize(sceneId);
    if (!id) throw new Error("Scene ID is required");
    project.scenes[id] = { text: text.trim() || "(empty scene)", choices: project.scenes[id]?.choices || [] };
    addWord("nouns", id);
  };

  const addChoice = (from, text, to, trigger) => {
    const f = normalize(from), t = normalize(to), tr = normalize(trigger);
    if (!project.scenes[f]) throw new Error(`From scene not found: ${f}`);
    if (!project.scenes[t]) throw new Error(`Target scene not found: ${t}`);
    project.scenes[f].choices.push({
      text: text.trim() || `Go to ${t}`,
      target_scene: t,
      trigger: tr || null
    });
  };

  const resolveCommand = (sceneId, command) => {
    const cmd = normalize(command);
    if (!cmd) return sceneId;
    const scene = project.scenes[sceneId];
    if (!scene) return "START";

    if (cmd.startsWith("CHOOSE ")) {
      const idx = Number(cmd.split(/\s+/)[1]) - 1;
      if (Number.isInteger(idx) && idx >= 0 && idx < scene.choices.length) {
        return scene.choices[idx].target_scene;
      }
      return sceneId;
    }

    const parts = cmd.split(/\s+/);
    if (parts.length >= 2) {
      const [verb, noun] = parts;
      if (project.dictionary.verbs.includes(verb) && project.dictionary.nouns.includes(noun)) {
        const trigger = `${verb} ${noun}`;
        const hit = scene.choices.find(c => normalize(c.trigger) === trigger);
        if (hit) return hit.target_scene;
      }
    }

    return sceneId;
  };

  const renderDictionary = () => {
    el("dictionaryView").textContent = JSON.stringify(project.dictionary, null, 2);
  };

  const renderPlay = () => {
    const scene = project.scenes[currentScene] || project.scenes.START;
    if (!project.scenes[currentScene]) currentScene = "START";

    el("sceneView").innerHTML = `<h3>[${currentScene}]</h3><p>${scene.text}</p>`;

    const choicesWrap = el("choiceButtons");
    choicesWrap.innerHTML = "";
    scene.choices.forEach((c, i) => {
      const b = document.createElement("button");
      b.textContent = `${i + 1}. ${c.text} -> ${c.target_scene}${c.trigger ? ` (${c.trigger})` : ""}`;
      b.addEventListener("click", () => {
        currentScene = c.target_scene;
        renderPlay();
      });
      choicesWrap.appendChild(b);
    });
  };

  const downloadProject = () => {
    const blob = new Blob([JSON.stringify(project, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${normalize(project.title || "story-machine") || "story-machine"}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const reset = () => {
    project = defaultProject(el("title").value || "Story Machine Modern");
    currentScene = "START";
    el("playLog").textContent = "";
    renderDictionary();
    renderPlay();
    status("New project initialized.");
  };

  el("newProjectBtn").addEventListener("click", reset);
  el("downloadBtn").addEventListener("click", downloadProject);

  el("loadInput").addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    project = JSON.parse(text);
    project.dictionary.verbs = project.dictionary.verbs || [];
    project.dictionary.nouns = project.dictionary.nouns || [];
    project.dictionary.articles = project.dictionary.articles || [];
    el("title").value = project.title || "Story Machine Modern";
    currentScene = "START";
    renderDictionary();
    renderPlay();
    status(`Loaded ${file.name}`);
  });

  el("addSceneBtn").addEventListener("click", () => {
    try {
      addScene(el("sceneId").value, el("sceneText").value);
      renderDictionary();
      renderPlay();
      status(`Scene ${normalize(el("sceneId").value)} saved.`);
    } catch (err) {
      status(err.message);
    }
  });

  el("addChoiceBtn").addEventListener("click", () => {
    try {
      addChoice(el("fromScene").value, el("choiceText").value, el("toScene").value, el("trigger").value);
      renderPlay();
      status("Choice added.");
    } catch (err) {
      status(err.message);
    }
  });

  el("addWordBtn").addEventListener("click", () => {
    addWord(el("dictCategory").value, el("dictWord").value);
    renderDictionary();
    status(`Added ${normalize(el("dictWord").value)} to ${el("dictCategory").value}`);
  });

  el("runCommandBtn").addEventListener("click", () => {
    const cmd = el("commandInput").value;
    if (!cmd.trim()) return;
    const next = resolveCommand(currentScene, cmd);
    log(`> ${cmd}`);
    if (next !== currentScene) log(`Moved ${currentScene} -> ${next}`);
    else log("No change.");
    currentScene = next;
    renderPlay();
  });

  el("lookBtn").addEventListener("click", renderPlay);
  el("helpBtn").addEventListener("click", () => log("Use CHOOSE <n> or VERB NOUN (example: GO FOREST)."));
  el("resetPlayBtn").addEventListener("click", () => { currentScene = "START"; renderPlay(); log("Reset to START."); });

  renderDictionary();
  renderPlay();
})();
