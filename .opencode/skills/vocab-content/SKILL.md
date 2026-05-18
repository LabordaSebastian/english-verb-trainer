---
name: vocab-content
description: Instructions for adding vocabulary topics (theory + quiz activities) to the English Verb Trainer
---

## When to use

Use this skill whenever you are asked to add new vocabulary content — theory, quiz activities, or both — to the English Verb Trainer SPA (`static/index.html`).

## Architecture overview

All vocab content lives in `static/index.html`. The app uses these patterns:

```
screen-vocab-menu        ← list of topics (e.g. "Giving My Opinion")
  └── screen-{topic}     ← sub-menu with Theory + Quiz buttons
        ├── screen-{topic}-theory  ← accordion theory (vocabTheoryData)
        └── screen-{topic}-quiz-select ← activity list (vocabActivities)
              └── screen-vocab-quiz ← renders MCQ or unscramble questions
```

### Data structures

**Theory** (accordion cards):
```js
const vocabTheoryData = [
  // Flat list of phrases:
  { name: "1. Section Title", phrases: ["item", "item", ...] },
  // With subsections:
  { name: "2. Section Title", subsections: [
    { title: "Subtitle:", phrases: ["item", ...] },
  ]},
];
```

**Quiz activities** (5 available activities, but a topic may have 0-N):
```js
const vocabActivities = [
  { id: "b1", title: "1. Activity Name", desc: "Short description" },
  // each activity gets a unique prefix like "b1", "b2"...
];
```

**Quiz questions** (two types):
```js
// Multiple choice:
{ id: "b1_q1", type: "mcq", question: "...", options: ["A", "B", "C"], correct: 0 },

// Unscramble (text input):
{ id: "b1_q2", type: "unscramble", question: "Put the words in order:", words: ["word1", "word2", ...], correct: "Full sentence." },

// Special: MCQ where any option is valid:
{ id: "b2_q1", type: "mcq", question: "...", options: ["A", "B", "C"], correct: 0, acceptAny: true },
```

## Adding a new vocabulary topic

### Step 1 — Ask the user

Ask: **"Does this topic have quiz activities or just theory?"** (single choice)
- **Theory only** → go to Step 2A
- **Theory + Quiz** → go to Step 2B

### Step 2A — Topic with ONLY theory

1. **Add a button** in `screen-vocab-menu`:

```html
<div style="width:100%;display:flex;flex-direction:column;gap:16px">
  <!-- existing buttons stay -->
  <button class="btn btn-home" id="btn-vocab-{topic}">
    <svg class="icon icon-lg"><use href="#icon-{icon}"/></svg>
    {Topic Title}
  </button>
</div>
```

2. **Add a theory screen** (after the last existing vocab screen):

```html
<!-- ── {TOPIC} THEORY ────────────────────────── -->
<div id="screen-vocab-{topic}-theory" class="screen">
  <div class="logo" style="font-size:28px"><svg class="icon icon-lg"><use href="#icon-book"/></svg> {Topic Title}</div>
  <div style="font-size:14px;color:var(--muted);margin-bottom:8px;text-align:center;">{Subtitle}</div>
  <div style="width:100%;max-height:65vh;overflow-y:auto;padding-right:4px;" id="vocab-{topic}-theory-list">
  </div>
  <button class="btn btn-secondary" id="btn-vocab-{topic}-theory-home" style="margin-top:16px;">← Back</button>
</div>
```

3. **Add theory data** to `vocabTheoryData` array (append at the end):

```js
{
  name: "1. Section Title",
  phrases: ["Phrase 1", "Phrase 2", ...],
},
```

If section has sub-sections, use `subsections` instead of `phrases`.

4. **Add a listener** in the Event Listeners section:

```js
document.getElementById('btn-vocab-{topic}').addEventListener('click', () => {
  showScreen('vocab-{topic}-menu');
});
// If no sub-menu (direct to theory):
document.getElementById('btn-vocab-{topic}').addEventListener('click', () => {
  if (document.getElementById('vocab-{topic}-theory-list').children.length === 0) {
    renderVocabTheory();
  }
  showScreen('vocab-{topic}-theory');
});
document.getElementById('btn-vocab-{topic}-theory-home').addEventListener('click', () => showScreen('vocab-menu'));
```

5. **If no sub-menu is needed** (direct to theory), add a back listener:

```js
document.getElementById('btn-vocab-{topic}-theory-home').addEventListener('click', () => showScreen('vocab-menu'));
```

### Step 2B — Topic with theory AND quiz

Follow Step 2A for the theory part. Additionally:

1. **Add a sub-menu screen** (after the vocab-menu screen or after the last topic screen):

```html
<!-- ── {TOPIC} MENU ──────────────────────────── -->
<div id="screen-vocab-{topic}" class="screen">
  <div class="logo" style="font-size:28px"><svg class="icon icon-lg"><use href="#icon-{icon}"/></svg> {Topic Title}</div>
  <div style="font-size:14px;color:var(--muted);margin-bottom:8px;text-align:center;">{Subtitle}</div>

  <div style="width:100%;display:flex;flex-direction:column;gap:16px">
    <button class="btn btn-home" id="btn-vocab-{topic}-theory">
      <svg class="icon icon-lg"><use href="#icon-book"/></svg>
      Theory
    </button>
    <button class="btn btn-home" id="btn-vocab-{topic}-quiz">
      <svg class="icon icon-lg"><use href="#icon-target"/></svg>
      Quiz
    </button>
  </div>

  <button class="btn btn-secondary btn-sm" id="btn-vocab-{topic}-home">← Back</button>
</div>
```

2. **Update the button in `screen-vocab-menu`** to point to the sub-menu instead:

```html
<button class="btn btn-home" id="btn-vocab-{topic}">
  <svg class="icon icon-lg"><use href="#icon-{icon}"/></svg>
  {Topic Title}
</button>
```

3. **Add a quiz-select screen** (after the theory screen):

```html
<!-- ── {TOPIC} QUIZ SELECT ───────────────────── -->
<div id="screen-vocab-{topic}-quiz-select" class="screen">
  <div class="logo" style="font-size:28px"><svg class="icon icon-lg"><use href="#icon-target"/></svg> {Topic Title} — Quiz</div>
  <div style="font-size:14px;color:var(--muted);margin-bottom:8px;text-align:center;">Choose an activity to practice</div>

  <div id="vocab-{topic}-activity-list" style="width:100%;display:flex;flex-direction:column;gap:12px">
  </div>

  <button class="btn btn-secondary btn-sm" id="btn-vocab-{topic}-quiz-select-home">← Back</button>
</div>
```

4. **Add activities** to the `vocabActivities` array (append at end):

```js
{ id: "b1", title: "1. Activity Name", desc: "Short description" },
{ id: "b2", title: "2. Another Activity", desc: "Short description" },
// ... increment prefix letter: a→b→c→d...
```

5. **Add questions** to the `opinionQuizData` array (append at end):

```js
// ── {Topic}: Activity 1 (MCQ) ──
{
  id: "b1_q1",
  type: "mcq",
  question: "Question text?",
  options: ["A", "B", "C"],
  correct: 0,
},
// ── {Topic}: Activity 2 (unscramble) ──
{
  id: "b2_q1",
  type: "unscramble",
  question: "Put the words in order:",
  words: ["word1", "word2", "word3"],
  correct: "The full correct sentence.",
},
```

6. **Add a render function** (before `vocabActivities`):

```js
function renderVocab{topic}QuizSelect() {
  const container = document.getElementById('vocab-{topic}-activity-list');
  container.innerHTML = vocabActivities.filter(a => a.id.startsWith('b')).map(a => `
    <button class="btn btn-home" onclick="startVocabQuiz('${a.id}')" style="text-align:left;justify-content:flex-start;gap:16px">
      <div style="display:flex;flex-direction:column;align-items:flex-start;gap:2px">
        <div style="font-size:16px;font-weight:600">${a.title}</div>
        <div style="font-size:13px;font-weight:400;color:var(--muted)">${a.desc}</div>
      </div>
    </button>
  `).join('');
}
```

Note: The filter `a.id.startsWith('b')` must use the correct prefix letter for your topic.

7. **Add listeners** in the Event Listeners section:

```js
document.getElementById('btn-vocab-{topic}').addEventListener('click', () => {
  showScreen('vocab-{topic}');
});
document.getElementById('btn-vocab-{topic}-theory').addEventListener('click', () => {
  if (document.getElementById('vocab-{topic}-theory-list').children.length === 0) {
    renderVocabTheory();
  }
  showScreen('vocab-{topic}-theory');
});
document.getElementById('btn-vocab-{topic}-quiz').addEventListener('click', () => {
  renderVocab{topic}QuizSelect();
  showScreen('vocab-{topic}-quiz-select');
});
document.getElementById('btn-vocab-{topic}-home').addEventListener('click', () => showScreen('vocab-menu'));
document.getElementById('btn-vocab-{topic}-theory-home').addEventListener('click', () => showScreen('vocab-{topic}'));
document.getElementById('btn-vocab-{topic}-quiz-select-home').addEventListener('click', () => showScreen('vocab-{topic}'));
```

## Adding quiz activities to an EXISTING topic that already has theory

If the topic already exists (has theory) and you're adding quiz activities for the first time:

1. **Add a sub-menu screen** between the vocab-menu and theory screens
2. **Move the theory screen's back button** to point to the sub-menu instead of vocab-menu
3. **Add the quiz-select screen** after the theory screen
4. **Update the vocab-menu button** to point to the sub-menu instead of directly to theory
5. **Add activities, questions, render function, and listeners** as in Step 2B items 4-7

## Question types reference

### MCQ (multiple choice)
```js
{
  id: "{prefix}_{num}",
  type: "mcq",
  question: "Displayed question text",
  options: ["Option A", "Option B", "Option C"],
  correct: 0,  // index of correct option (0-based)
  acceptAny: true,  // optional: marks any option as correct
}
```

### Unscramble (text input)
```js
{
  id: "{prefix}_{num}",
  type: "unscramble",
  question: "Put the words in order to form a question/sentence:",
  words: ["word1", "word2", "word3", "word4"],  // shown as pills
  correct: "The full correct sentence.",  // compared case-insensitively, ignoring punctuation
}
```

## Activity ID prefix convention

The quiz filtering uses ID prefixes to match activities to questions:

| Prefix | Example ID | Questions in that activity |
|--------|-----------|--------------------------|
| a1-a5  | a2_q3     | "Giving My Opinion" activities |
| b1-bN  | b1_q2     | Next topic's activities |
| c1-cN  | c1_q1     | Third topic's activities |

Use sequential letters for each new topic that has quizzes.

## Common pitfalls

- **ID collision**: Ensure question IDs are unique across the entire `opinionQuizData` array
- **Activity prefix mismatch**: The `vocabActivities` entry `id` and question IDs must share the same prefix (e.g. `b1` → `b1_q1`, `b1_q2`)
- **Filters**: The `renderVocab{topic}QuizSelect()` filter must match the correct prefix letter
- **Unscramble normalization**: The `normalize()` function strips punctuation and collapses spaces, so the `correct` field should use standard punctuation but will match without it
- **Back navigation**: Every new screen needs a back button, and the back button's target must go to the correct parent screen
