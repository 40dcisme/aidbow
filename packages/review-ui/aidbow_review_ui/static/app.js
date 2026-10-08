/* aidbow review-ui · 评审决策台前端（原生 JS，零外链）
 *
 * 数据契约见 SPEC.md §1；状态结构与 aidbow_review_ui/decision_export.py 一致：
 *   state[id] = {picked:bool, priority:"P0|P1|P2|shelved|''", note:str}
 */
(function () {
  "use strict";

  var IDEAS = window.__AIDBOW_IDEAS__ || [];
  var DEMAND_ID = window.__AIDBOW_DEMAND_ID__ || "demand";
  var STORE_KEY = "aidbow-review-ui:" + DEMAND_ID;
  var P_ORDER = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"];
  var PRIORITIES = [
    { v: "P0", label: "P0 · 立即做" },
    { v: "P1", label: "P1 · 本轮做" },
    { v: "P2", label: "P2 · 排期做" },
    { v: "shelved", label: "搁置" }
  ];

  /* ---------- 状态持久化 ---------- */
  var store = {};
  try {
    store = JSON.parse(localStorage.getItem(STORE_KEY) || "{}") || {};
  } catch (e) {
    store = {}; // localStorage 损坏时不阻断页面
  }
  function getState(id) {
    if (!store[id]) store[id] = { picked: false, priority: "", note: "" };
    return store[id];
  }
  function save() {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(store));
    } catch (e) { /* 隐私模式等场景：仅本次会话有效 */ }
  }

  /* ---------- 工具 ---------- */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function el(tag, attrs, html) {
    var node = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "class") node.className = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    if (html != null) node.innerHTML = html;
    return node;
  }

  /* ---------- 渲染 ---------- */
  var listNode = document.getElementById("list");
  var nPickedNode = document.getElementById("nPicked");
  var nNoteNode = document.getElementById("nNote");
  var totalNode = document.getElementById("nTotal");
  totalNode.textContent = IDEAS.length;

  function pBadges(idea) {
    return P_ORDER.filter(function (k) {
      return idea.P[k] !== undefined && idea.P[k] !== null;
    }).map(function (k) {
      var v = idea.P[k];
      return '<span class="pv ' + (v >= 4 ? "hi" : "") + '">' +
        k + " " + esc(String(v)) + "</span>";
    }).join("");
  }

  function basisText(idea) {
    var rows = P_ORDER.filter(function (k) { return idea.basis && idea.basis[k]; })
      .map(function (k) { return "· " + k + "：" + esc(idea.basis[k]); });
    return rows.length ? "【评分依据】\n" + rows.join("\n") : "";
  }

  function makeCard(idea) {
    var st = getState(idea.id);
    var card = el("article", {
      "class": "card" + (st.picked ? " picked" : (st.priority === "shelved" ? " dim" : "")),
      "data-id": idea.id,
      "data-round": idea.round
    });

    /* 头部：勾选框 + 标题 + 元信息 */
    var head = el("div", { "class": "chead" });
    var cb = el("input", { type: "checkbox", "class": "cb", "data-id": idea.id });
    cb.checked = !!st.picked;
    head.appendChild(cb);

    var metaBits = [
      '<span class="tag">' + esc(idea.id) + "</span>",
      '<span class="tag">' + esc(idea.author) + "</span>",
      '<span class="tag ' + idea.round.toLowerCase() + '">' + idea.round + "</span>"
    ];
    if (idea.lineage) {
      metaBits.push('<span class="tag lineage">' + esc(idea.lineage.mode) +
        " ← " + esc(idea.lineage["from"]) + "</span>");
    }
    var ttl = el("div", { "class": "ttl" },
      '<div class="t">' + esc(idea.title) + "</div>" +
      '<div class="one">一句话核心：' + esc(idea.oneLiner) + "</div>" +
      '<div class="meta">' + metaBits.join("") + "</div>" +
      '<div class="pvrow">' + pBadges(idea) + "</div>");
    head.appendChild(ttl);
    card.appendChild(head);

    /* 正文（默认折叠） */
    var bodyWrap = el("div", { "class": "body" });
    var toggle = el("button", { type: "button", "class": "toggle" },
      "▸ 展开正文（" + idea.body.length + " 字）");
    var txt = el("div", { "class": "txt" });
    txt.style.whiteSpace = "pre-wrap";
    txt.textContent = idea.body + (basisText(idea) ? "\n\n" + basisText(idea) : "");
    bodyWrap.appendChild(toggle);
    bodyWrap.appendChild(txt);
    card.appendChild(bodyWrap);

    /* 决策行：优先级 + 备注 */
    var row = el("div", { "class": "pickrow" });
    var sel = el("select", { "class": "prio", "data-id": idea.id });
    sel.appendChild(el("option", { value: "" }, "优先级：未定"));
    PRIORITIES.forEach(function (p) {
      var o = el("option", { value: p.v }, p.label);
      if (st.priority === p.v) o.selected = true;
      sel.appendChild(o);
    });
    row.appendChild(sel);
    var note = el("textarea", {
      "class": "note",
      "data-id": idea.id,
      rows: "1",
      placeholder: "备注：为什么选/不选、要改什么、约束……"
    });
    note.value = st.note || "";
    row.appendChild(note);
    card.appendChild(row);
    return card;
  }

  function render() {
    var fr = document.getElementById("fRound").value;
    var fa = document.getElementById("fAuthor").value;
    var onlyPicked = document.getElementById("fPicked").classList.contains("on");
    listNode.innerHTML = "";
    IDEAS.filter(function (it) {
      var st = getState(it.id);
      if (fr && it.round !== fr) return false;
      if (fa && it.author !== fa) return false;
      if (onlyPicked && !st.picked) return false;
      return true;
    }).forEach(function (it) { listNode.appendChild(makeCard(it)); });
    updateStats();
  }

  function updateStats() {
    var np = 0, nn = 0;
    IDEAS.forEach(function (it) {
      var st = getState(it.id);
      if (st.picked) np++;
      if (st.note && st.note.trim()) nn++;
    });
    nPickedNode.textContent = np;
    nNoteNode.textContent = nn;
  }

  /* ---------- 决策单导出（Markdown / JSON，口径同 decision_export.py） ---------- */
  function buildDecision() {
    var d = { demandId: DEMAND_ID, selected: [], priorities: {}, notes: {} };
    IDEAS.forEach(function (it) {
      var st = getState(it.id);
      if (st.picked) d.selected.push(it.id);
      if (st.priority) d.priorities[it.id] = st.priority;
      if (st.note && st.note.trim()) d.notes[it.id] = st.note.trim();
    });
    if (!Object.keys(d.priorities).length) delete d.priorities;
    if (!Object.keys(d.notes).length) delete d.notes;
    return d;
  }

  function prioLabel(v) {
    var hit = PRIORITIES.filter(function (p) { return p.v === v; })[0];
    return hit ? hit.label : v;
  }

  function buildMarkdown() {
    var when = new Date().toLocaleString();
    var picked = [], drafted = [], shelved = [];
    IDEAS.forEach(function (it) {
      var st = getState(it.id);
      if (st.picked) picked.push(it);
      else if (st.priority === "shelved") shelved.push(it);
      else if (st.priority) drafted.push(it);
    });

    var L = [
      "# 评审决策单 · " + DEMAND_ID,
      "> Demand `" + DEMAND_ID + "` ｜ 决策时间 " + when +
        " ｜ 共 " + IDEAS.length + " 条 · 选中 " + picked.length + " 条",
      "> 口径：✅ 选中 = 纳入执行候选；🕓 备选 = 已定优先级未勾选；⏸ 搁置 = 暂缓。",
      "---"
    ];

    function section(tag, items) {
      if (!items.length) return;
      L.push("## " + tag + "（" + items.length + "）");
      items.forEach(function (it) {
        var st = getState(it.id);
        var head = st.priority ? "[" + prioLabel(st.priority) + "] " : "";
        L.push("### " + head + it.title);
        L.push("- **编号**：" + it.id + " ｜ **作者**：" + it.author +
          " ｜ **轮次**：" + it.round);
        var pvals = P_ORDER.filter(function (k) { return it.P[k] !== undefined; })
          .map(function (k) { return k + "=" + it.P[k]; }).join(" ");
        L.push("- **P 值**：" + (pvals || "（未评分）"));
        L.push("- **一句话核心**：" + it.oneLiner);
        if (it.lineage) {
          L.push("- **递进来源**：" + it.lineage.mode + " ← " + it.lineage["from"]);
        }
        if (st.note && st.note.trim()) L.push("- **决策备注**：" + st.note.trim());
        L.push("");
      });
      L.push("---");
    }
    section("✅ 选中（纳入执行候选）", picked);
    section("🕓 备选（已定优先级未勾选）", drafted);
    section("⏸ 搁置", shelved);
    if (!picked.length && !drafted.length && !shelved.length) {
      L.push("> ⚠️ 尚未做出任何决策（未勾选 / 未标优先级）。");
    }
    L.push("_由 aidbow review-ui 决策台生成 · " + when + "_");
    return L.join("\n");
  }

  function download(filename, text, mime) {
    var blob = new Blob([text], { type: mime || "text/plain" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  function showOutput(title, text) {
    var dlg = document.getElementById("dlg");
    document.getElementById("dlgTitle").textContent = title;
    document.getElementById("outText").value = text;
    if (typeof dlg.showModal === "function") dlg.showModal();
    else window.prompt(title, text); // 兜底
  }

  /* ---------- 事件委托 ---------- */
  listNode.addEventListener("click", function (e) {
    var t = e.target;
    if (t.classList.contains("cb")) {
      getState(t.getAttribute("data-id")).picked = t.checked;
      save();
      var card = t.closest(".card");
      card.classList.toggle("picked", t.checked);
      updateStats();
    } else if (t.classList.contains("toggle")) {
      var body = t.closest(".body");
      var open = body.classList.toggle("open");
      t.textContent = open ? "▾ 收起正文" :
        "▸ 展开正文（" + t.parentNode.querySelector(".txt").textContent.length + " 字）";
    }
  });
  listNode.addEventListener("change", function (e) {
    if (e.target.classList.contains("prio")) {
      getState(e.target.getAttribute("data-id")).priority = e.target.value;
      save();
      var card = e.target.closest(".card");
      card.classList.toggle("dim", e.target.value === "shelved" &&
        !card.classList.contains("picked"));
    }
  });
  listNode.addEventListener("input", function (e) {
    if (e.target.classList.contains("note")) {
      getState(e.target.getAttribute("data-id")).note = e.target.value;
      save();
      updateStats();
    }
  });

  /* 作者筛选选项 */
  var fAuthor = document.getElementById("fAuthor");
  Array.prototype.forEach.call(
    Array.prototype.filter.call(IDEAS, function (v, i, a) {
      return a.map(function (x) { return x.author; }).indexOf(v.author) === i;
    }),
    function (it) { fAuthor.appendChild(el("option", { value: it.author }, it.author)); }
  );

  document.getElementById("fRound").addEventListener("change", render);
  fAuthor.addEventListener("change", render);
  document.getElementById("fPicked").addEventListener("click", function (e) {
    e.target.classList.toggle("on");
    render();
  });
  document.getElementById("fClear").addEventListener("click", function () {
    if (window.confirm("清空所有勾选？（优先级与备注保留）")) {
      IDEAS.forEach(function (it) { getState(it.id).picked = false; });
      save();
      render();
    }
  });

  document.getElementById("doMd").addEventListener("click", function () {
    showOutput("评审决策单 · Markdown", buildMarkdown());
  });
  document.getElementById("doJson").addEventListener("click", function () {
    showOutput("评审决策单 · Decision JSON",
      JSON.stringify(buildDecision(), null, 2));
  });
  document.getElementById("doDownloadMd").addEventListener("click", function () {
    download(DEMAND_ID + "-decision.md", buildMarkdown(), "text/markdown");
  });
  document.getElementById("doDownloadJson").addEventListener("click", function () {
    download(DEMAND_ID + "-decision.json",
      JSON.stringify(buildDecision(), null, 2), "application/json");
  });
  document.getElementById("doCopy").addEventListener("click", function () {
    var text = document.getElementById("outText").value;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        document.getElementById("copyState").textContent = "已复制 ✓";
      }, function () {
        document.getElementById("outText").select();
      });
    } else {
      document.getElementById("outText").select();
    }
  });

  render();
})();
