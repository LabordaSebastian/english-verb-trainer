# Plan: 1000 Palabras Más Comunes del Inglés

## Constraints
- **Exclude** all irregular verb base forms from vocabulary words
- **No repeated options** in MCQ questions — each option must be unique
- **Max quiz size = category size** — if a category has 80 words, max quiz is 80

## Irregular Verbs to Exclude (100 base forms)
be, have, do, go, say, get, make, know, think, take, see, come, give, find, tell, feel, become, leave, put, mean, keep, let, begin, show, hear, run, bring, write, sit, stand, lose, pay, meet, set, lead, understand, speak, read, spend, cut, send, build, grow, fall, hold, buy, drive, break, learn, forget, catch, fight, teach, sell, choose, sleep, win, hang, draw, fly, wear, throw, steal, hide, shake, wake, rise, bite, swim, sing, ring, drink, eat, feed, lend, bend, burn, dream, kneel, sweep, weep, creep, leap, deal, knit, hit, hurt, cost, spread, shed, split, beat, forbid, forgive, undertake, overcome, withdraw, mistake, arise, bind

---

## 1. Database Models — `app/models.py`

Add two new tables after `UserAttempt`:

```python
class VocabularyWord(Base):
    __tablename__ = "vocabulary_words"
    id = Column(Integer, primary_key=True, index=True)
    english = Column(String(100), unique=True, nullable=False, index=True)
    spanish = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    attempts: Mapped[list["VocabAttempt"]] = relationship(
        "VocabAttempt", back_populates="word", cascade="all, delete-orphan"
    )

class VocabAttempt(Base):
    __tablename__ = "vocab_attempts"
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("vocabulary_words.id"), nullable=False)
    answer_given = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    word: Mapped[Optional["VocabularyWord"]] = relationship(
        "VocabularyWord", back_populates="attempts"
    )
```

---

## 2. Vocabulary Seed Data — `app/vocab_seed.py`

New file with 1000 words in 10 categories (~100 each):

| # | Category | Count | Examples |
|---|---|---|---|
| 1 | Pronouns & Determiners | ~80 | I, you, he, she, it, we, they, this, that, my, your, the, a, an, some, any, all, each, every... |
| 2 | Prepositions | ~60 | in, on, at, to, from, with, without, for, about, by, through, during, before, after, above, below... |
| 3 | Conjunctions & Connectors | ~50 | and, but, or, so, because, if, when, while, although, however, therefore, moreover, nevertheless... |
| 4 | Common Verbs (regular) | ~200 | ask, answer, call, carry, change, check, clean, close, cook, copy, count, cover, cross, dance, decide... |
| 5 | Adjectives | ~150 | good, new, first, last, long, great, little, own, other, old, right, big, high, different, small, large... |
| 6 | Adverbs | ~100 | not, also, very, just, only, even, still, already, always, never, sometimes, often, usually, really... |
| 7 | Common Nouns | ~200 | time, person, year, way, day, thing, man, woman, world, life, hand, place, case, week, company, system... |
| 8 | Numbers & Quantifiers | ~60 | one, two, three, hundred, thousand, first, second, many, much, more, most, few, several, both... |
| 9 | Question Words | ~50 | what, who, whom, whose, which, where, when, why, how, how much, how many, how often, how long... |
| 10 | Common Phrases | ~50 | of course, in fact, at least, a lot of, instead of, because of, in front of, next to, kind of... |

Format:
```python
VOCABULARY_WORDS = [
    # (english, spanish, category)
    ("apple", "manzana", "Common Nouns"),
    ("beautiful", "hermoso/a", "Adjectives"),
    ...
]

def seed_vocabulary(db: Session) -> tuple[int, int]:
    """Upsert vocabulary words. Returns (added, updated)."""
```

---

## 3. CLI Command — `app/cli.py`

Add new command:

```python
@app.command(name="vocab-seed")
def vocab_seed():
    """Load the 1000 most common English words into the database."""
    _init_db()
    db = SessionLocal()
    try:
        added, updated = seed_vocabulary(db)
        typer.echo(f"\n  {added} word(s) added, {updated} updated.\n")
    finally:
        db.close()
```

---

## 4. API Schemas — `api/schemas.py`

Add:

```python
class VocabQuizWord(BaseModel):
    id: int
    english: str
    category: str

class VocabAttemptRequest(BaseModel):
    word_id: int = Field(..., gt=0)
    answer_given: str

class VocabAttemptResponse(BaseModel):
    correct: bool
    correct_answer: str

class VocabStatsResponse(BaseModel):
    total: int
    correct: int
    wrong: int
    accuracy: float
    hardest_words: list[HardestWord]

class HardestWord(BaseModel):
    word: str
    spanish: str
    errors: int

class VocabSeedResponse(BaseModel):
    added: int
    updated: int

class VocabCategory(BaseModel):
    name: str
    count: int
```

---

## 5. API Endpoints — `api/main.py`

Add after existing endpoints:

```python
@app.get("/api/vocab/categories", response_model=list[VocabCategory], tags=["vocab"])
def get_vocab_categories(db: Session = Depends(get_db)):
    """Return available vocabulary categories with word counts."""

@app.get("/api/vocab/quiz", response_model=list[VocabQuizWord], tags=["vocab"])
def get_vocab_quiz_words(
    count: int = 10,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Return N shuffled vocabulary words for a quiz."""

@app.post("/api/vocab/attempts", response_model=VocabAttemptResponse, tags=["vocab"])
def submit_vocab_attempt(attempt: VocabAttemptRequest, db: Session = Depends(get_db)):
    """Validate a vocabulary answer and log the attempt."""

@app.get("/api/vocab/stats", response_model=VocabStatsResponse, tags=["vocab"])
def get_vocab_stats(db: Session = Depends(get_db)):
    """Return vocabulary quiz statistics."""

@app.post("/api/vocab/seed", response_model=VocabSeedResponse, tags=["vocab-admin"])
def seed_vocab_endpoint(db: Session = Depends(get_db)):
    """Seed or refresh the 1000 vocabulary words."""
```

---

## 6. Frontend Screens — `static/index.html`

### New Screens (HTML)

```html
<!-- VOCABULARY WORDS MENU -->
<div id="screen-vocab-words-menu" class="screen">
  <div class="logo" style="font-size:28px">
    <svg class="icon icon-lg"><use href="#icon-book"/></svg> Vocabulary Words
  </div>
  <div class="subtitle">Practice the 1000 most common English words</div>
  
  <div class="card" style="width:100%;max-height:50vh;overflow-y:auto;">
    <div id="vocab-words-category-list" style="display:flex;flex-direction:column;gap:10px;">
    </div>
  </div>
  
  <button class="btn btn-secondary btn-sm" id="btn-vocab-words-menu-home">← Back</button>
</div>

<!-- VOCABULARY WORDS QUIZ SELECT -->
<div id="screen-vocab-words-quiz-select" class="screen">
  <div class="logo" style="font-size:28px">
    <svg class="icon icon-lg"><use href="#icon-target"/></svg> Vocabulary Quiz
  </div>
  <div class="subtitle" id="vocab-words-selected-category">Category: All</div>
  
  <div class="card" style="text-align:center;">
    <div style="font-size:15px;font-weight:600;margin-bottom:12px">How many questions?</div>
    <div class="rounds-row" id="vocab-words-rounds-row">
      <!-- Dynamically populated based on category size -->
    </div>
  </div>
  
  <button class="btn btn-primary" id="btn-start-vocab-words-quiz" style="width:100%;">
    <svg class="icon"><use href="#icon-play"/></svg> Start Quiz
  </button>
  
  <button class="btn btn-secondary btn-sm" id="btn-vocab-words-quiz-select-back">← Back</button>
</div>

<!-- VOCABULARY WORDS QUIZ -->
<div id="screen-vocab-words-quiz" class="screen">
  <div style="width:100%;display:flex;flex-direction:column;gap:6px">
    <div class="progress-label" id="vw-progress-label">Question 1 / 10</div>
    <div class="progress-wrap"><div class="progress-bar" id="vw-progress-bar" style="width:0%"></div></div>
  </div>
  
  <div class="card" style="display:flex;flex-direction:column;align-items:center;gap:20px;">
    <div style="width:100%;text-align:center;">
      <div style="font-size:14px;color:var(--muted);margin-bottom:8px;">Translate to English:</div>
      <div class="verb-base" id="vw-spanish-word">manzana</div>
      <div style="font-size:12px;color:var(--blue);margin-top:4px;" id="vw-category-label">Common Nouns</div>
    </div>
    
    <div style="width:100%;">
      <label class="input-label" for="vw-input-answer">English word</label>
      <input class="input-field" id="vw-input-answer" type="text" placeholder="Type the English word..." autocomplete="off" spellcheck="false">
    </div>
    
    <div class="feedback" id="vw-feedback" role="alert"></div>
    
    <div class="action-row" style="width:100%">
      <button class="btn btn-primary" id="vw-btn-check" style="flex:1">Check ✓</button>
      <button class="btn btn-secondary" id="vw-btn-next" style="flex:1;display:none">Next →</button>
    </div>
  </div>
</div>

<!-- VOCABULARY WORDS RESULTS -->
<div id="screen-vocab-words-results" class="screen">
  <div class="logo" style="font-size:28px">
    <svg class="icon icon-lg"><use href="#icon-trophy"/></svg> Quiz Complete
  </div>
  
  <div class="card" style="display:flex;flex-direction:column;align-items:center;gap:24px;">
    <div class="score-circle">
      <div class="score-pct" id="vw-result-pct">0%</div>
      <div class="score-label" id="vw-result-label">0 / 0</div>
    </div>
    
    <div style="width:100%">
      <div style="font-size:13px;font-weight:600;color:var(--muted);text-transform:uppercase;margin-bottom:12px">Mistakes</div>
      <div class="wrong-list" id="vw-wrong-list">
        <div class="empty">Perfect score. No mistakes.</div>
      </div>
    </div>
  </div>
  
  <div class="action-row">
    <button class="btn btn-primary" id="btn-vw-play-again"><svg class="icon"><use href="#icon-play"/></svg> Play Again</button>
    <button class="btn btn-secondary" id="btn-vw-stats"><svg class="icon"><use href="#icon-chart"/></svg> Stats</button>
    <button class="btn btn-secondary" id="btn-vw-results-home">← Back</button>
  </div>
</div>

<!-- VOCABULARY WORDS STATS -->
<div id="screen-vocab-words-stats" class="screen">
  <div class="logo" style="font-size:28px">
    <svg class="icon icon-lg"><use href="#icon-chart"/></svg> Vocabulary Stats
  </div>
  
  <div id="vw-stats-loading"><div class="spinner"></div></div>
  
  <div id="vw-stats-content" style="width:100%;display:none;flex-direction:column;gap:16px;">
    <div class="stat-row" style="grid-template-columns:1fr 1fr 1fr 1fr;">
      <div class="stat-box"><div class="stat-num" id="vw-s-total">0</div><div class="stat-name">Total</div></div>
      <div class="stat-box"><div class="stat-num" style="color:var(--green)" id="vw-s-correct">0</div><div class="stat-name">Correct</div></div>
      <div class="stat-box"><div class="stat-num" style="color:var(--red)" id="vw-s-wrong">0</div><div class="stat-name">Wrong</div></div>
      <div class="stat-box"><div class="stat-num" style="color:var(--purple)" id="vw-s-acc">0%</div><div class="stat-name">Accuracy</div></div>
    </div>
    
    <div class="card">
      <div style="font-size:13px;font-weight:600;color:var(--muted);text-transform:uppercase;margin-bottom:14px">
        <svg class="icon icon-sm"><use href="#icon-flame"/></svg> Most Missed Words
      </div>
      <div class="hardest-list" id="vw-hardest-list">
        <div class="empty">No mistakes yet.</div>
      </div>
    </div>
  </div>
  
  <button class="btn btn-secondary" id="btn-vw-stats-home">← Back</button>
</div>
```

### New JavaScript State & API

```javascript
// State
const vocabWordsState = {
  rounds: 10,
  words: [],       // [{id, english, category}]
  index: 0,
  correct: 0,
  wrongs: [],      // [{spanish, correct: english}]
  checked: false,
  selectedCategory: null,
};

// API functions
const apiVocabWords = {
  async getCategories() {
    const r = await fetch('/api/vocab/categories');
    return r.json();
  },
  async getWords(count, category) {
    const url = category 
      ? `/api/vocab/quiz?count=${count}&category=${encodeURIComponent(category)}`
      : `/api/vocab/quiz?count=${count}`;
    const r = await fetch(url);
    return r.json();
  },
  async submitAttempt(word_id, answer_given) {
    const r = await fetch('/api/vocab/attempts', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({word_id, answer_given}),
    });
    return r.json();
  },
  async getStats() {
    const r = await fetch('/api/vocab/stats');
    return r.json();
  },
  async seed() {
    const r = await fetch('/api/vocab/seed', {method: 'POST'});
    return r.json();
  },
};
```

### Quiz Logic (Key Functions)

```javascript
async function startVocabWordsQuiz() {
  const maxWords = vocabWordsState.words.length;
  const actualRounds = Math.min(vocabWordsState.rounds, maxWords);
  
  vocabWordsState.words = vocabWordsState.words.slice(0, actualRounds);
  vocabWordsState.words.sort(() => Math.random() - 0.5);
  vocabWordsState.index = 0;
  vocabWordsState.correct = 0;
  vocabWordsState.wrongs = [];
  
  showScreen('vocab-words-quiz');
  renderVocabWordsQuestion();
}

function renderVocabWordsQuestion() {
  const w = vocabWordsState.words[vocabWordsState.index];
  const total = vocabWordsState.words.length;
  const num = vocabWordsState.index + 1;
  
  document.getElementById('vw-spanish-word').textContent = w.spanish;
  document.getElementById('vw-category-label').textContent = w.category;
  document.getElementById('vw-progress-label').textContent = `Question ${num} / ${total}`;
  
  const input = document.getElementById('vw-input-answer');
  input.value = '';
  input.className = 'input-field';
  input.disabled = false;
  
  const fb = document.getElementById('vw-feedback');
  fb.className = 'feedback';
  fb.innerHTML = '';
  
  document.getElementById('vw-btn-check').style.display = '';
  document.getElementById('vw-btn-next').style.display = 'none';
  vocabWordsState.checked = false;
  input.focus();
}

async function checkVocabWordsAnswer() {
  if (vocabWordsState.checked) return;
  const answer = document.getElementById('vw-input-answer').value.trim();
  if (!answer) return;
  
  vocabWordsState.checked = true;
  const w = vocabWordsState.words[vocabWordsState.index];
  
  const result = await apiVocabWords.submitAttempt(w.id, answer);
  
  const input = document.getElementById('vw-input-answer');
  const fb = document.getElementById('vw-feedback');
  input.disabled = true;
  
  if (result.correct) {
    vocabWordsState.correct++;
    input.className = 'input-field correct';
    fb.className = 'feedback correct show';
    fb.innerHTML = `<svg class="icon icon-check"><use href="#icon-check"/></svg> Correct! <strong>${w.spanish} → ${w.english}</strong>`;
  } else {
    input.className = 'input-field wrong';
    fb.className = 'feedback wrong show';
    fb.innerHTML = `<svg class="icon icon-x"><use href="#icon-x"/></svg> Wrong! <strong>${w.spanish} → ${result.correct_answer}</strong>`;
    vocabWordsState.wrongs.push({spanish: w.spanish, correct: w.english, yourAnswer: answer});
  }
  
  document.getElementById('vw-btn-check').style.display = 'none';
  const nextBtn = document.getElementById('vw-btn-next');
  nextBtn.style.display = '';
  nextBtn.textContent = vocabWordsState.index + 1 < vocabWordsState.words.length ? 'Next →' : 'See Results';
}

function nextVocabWordsQuestion() {
  vocabWordsState.index++;
  if (vocabWordsState.index >= vocabWordsState.words.length) {
    showVocabWordsResults();
  } else {
    renderVocabWordsQuestion();
  }
}

function showVocabWordsResults() {
  const total = vocabWordsState.words.length;
  const pct = total > 0 ? Math.round((vocabWordsState.correct / total) * 100) : 0;
  
  document.getElementById('vw-result-pct').textContent = pct + '%';
  document.getElementById('vw-result-label').textContent = `${vocabWordsState.correct} / ${total} correct`;
  
  const list = document.getElementById('vw-wrong-list');
  if (vocabWordsState.wrongs.length === 0) {
    list.innerHTML = '<div class="empty">Perfect score. No mistakes.</div>';
  } else {
    list.innerHTML = vocabWordsState.wrongs.map(w =>
      `<div class="wrong-item">
        <span class="verb-name">${w.spanish}</span>
        <span class="correct-forms">Your answer: ${w.yourAnswer} → Correct: ${w.correct}</span>
      </div>`
    ).join('');
  }
  
  showScreen('vocab-words-results');
}

async function loadVocabWordsStats() {
  showScreen('vocab-words-stats');
  document.getElementById('vw-stats-loading').style.display = 'block';
  document.getElementById('vw-stats-content').style.display = 'none';
  
  const data = await apiVocabWords.getStats();
  
  document.getElementById('vw-s-total').textContent = data.total;
  document.getElementById('vw-s-correct').textContent = data.correct;
  document.getElementById('vw-s-wrong').textContent = data.wrong;
  document.getElementById('vw-s-acc').textContent = data.accuracy + '%';
  
  const maxErrors = data.hardest_words.length > 0 ? data.hardest_words[0].errors : 1;
  const hardestEl = document.getElementById('vw-hardest-list');
  
  if (data.hardest_words.length === 0) {
    hardestEl.innerHTML = '<div class="empty">No mistakes yet.</div>';
  } else {
    hardestEl.innerHTML = data.hardest_words.map(w =>
      `<div class="hardest-item">
        <span class="hardest-verb">${w.word.toUpperCase()}</span>
        <span style="color:var(--muted);font-size:12px;flex:1;">${w.spanish}</span>
        <div class="hardest-bar-wrap"><div class="hardest-bar" style="width:${(w.errors/maxErrors)*100}%"></div></div>
        <span class="hardest-count">${w.errors} error${w.errors>1?'s':''}</span>
      </div>`
    ).join('');
  }
  
  document.getElementById('vw-stats-loading').style.display = 'none';
  document.getElementById('vw-stats-content').style.display = 'flex';
}
```

### Event Listeners

```javascript
// Home screen -> Vocab Words menu
document.getElementById('btn-vocabulary-words').addEventListener('click', () => {
  showScreen('vocab-words-menu');
  loadVocabWordsCategories();
});

// Category selection
function loadVocabWordsCategories() {
  apiVocabWords.getCategories().then(categories => {
    const container = document.getElementById('vocab-words-category-list');
    container.innerHTML = `
      <button class="btn btn-home" onclick="selectVocabWordsCategory(null)">
        <svg class="icon icon-lg"><use href="#icon-star"/></svg>
        All Categories
      </button>
      ${categories.map(c => `
        <button class="btn btn-home" onclick="selectVocabWordsCategory('${c.name}')">
          <svg class="icon icon-lg"><use href="#icon-book"/></svg>
          ${c.name} <span style="color:var(--muted);font-size:13px;margin-left:auto;">(${c.count} words)</span>
        </button>
      `).join('')}
    `;
  });
}

function selectVocabWordsCategory(category) {
  vocabWordsState.selectedCategory = category;
  document.getElementById('vocab-words-selected-category').textContent = 
    category ? `Category: ${category}` : 'Category: All';
  
  // Determine available round options based on category size
  apiVocabWords.getCategories().then(categories => {
    let maxWords = categories.reduce((sum, c) => sum + c.count, 0);
    if (category) {
      const cat = categories.find(c => c.name === category);
      maxWords = cat ? cat.count : maxWords;
    }
    
    const roundsRow = document.getElementById('vocab-words-rounds-row');
    const options = [10, 25, 50, 75, 100].filter(n => n <= maxWords);
    if (options.length === 0) options.push(maxWords);
    
    roundsRow.innerHTML = options.map((n, i) => `
      <button class="round-btn ${i === 0 ? 'selected' : ''}" data-rounds="${n}">${n}</button>
    `).join('');
    
    // Re-attach listeners
    roundsRow.querySelectorAll('.round-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        roundsRow.querySelectorAll('.round-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        vocabWordsState.rounds = parseInt(btn.dataset.rounds);
      });
    });
    
    showScreen('vocab-words-quiz-select');
  });
}

// Start quiz
document.getElementById('btn-start-vocab-words-quiz').addEventListener('click', async () => {
  const btn = document.getElementById('btn-start-vocab-words-quiz');
  btn.disabled = true;
  btn.textContent = 'Loading...';
  
  try {
    vocabWordsState.words = await apiVocabWords.getWords(
      vocabWordsState.rounds, 
      vocabWordsState.selectedCategory
    );
  } catch (e) {
    showError(e.message);
    btn.disabled = false;
    btn.innerHTML = '<svg class="icon"><use href="#icon-play"/></svg> Start Quiz';
    return;
  }
  
  btn.disabled = false;
  btn.innerHTML = '<svg class="icon"><use href="#icon-play"/></svg> Start Quiz';
  startVocabWordsQuiz();
});

// Quiz controls
document.getElementById('vw-btn-check').addEventListener('click', checkVocabWordsAnswer);
document.getElementById('vw-btn-next').addEventListener('click', nextVocabWordsQuestion);
document.getElementById('btn-vw-play-again').addEventListener('click', () => showScreen('vocab-words-menu'));
document.getElementById('btn-vw-stats').addEventListener('click', loadVocabWordsStats);
document.getElementById('btn-vw-results-home').addEventListener('click', () => showScreen('vocab-words-menu'));
document.getElementById('btn-vw-stats-home').addEventListener('click', () => showScreen('vocab-words-menu'));
document.getElementById('btn-vocab-words-menu-home').addEventListener('click', () => showScreen('home'));
document.getElementById('btn-vocab-words-quiz-select-back').addEventListener('click', () => showScreen('vocab-words-menu'));

// Enter key support
document.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const quiz = document.getElementById('screen-vocab-words-quiz');
    if (!quiz.classList.contains('active')) return;
    if (!vocabWordsState.checked) checkVocabWordsAnswer();
    else nextVocabWordsQuestion();
  }
});
```

---

## 7. Dockerfile Update — `docker/Dockerfile`

Add copy for new file:

```dockerfile
COPY app/       ./app/
# Now includes vocab_seed.py automatically
```

No change needed — `COPY app/ ./app/` already copies everything.

---

## 8. Tests — `tests/test_vocab_api.py`

```python
"""Tests for vocabulary API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from app.database import Base, get_db
from app.models import VocabularyWord, VocabAttempt

# ... fixtures and tests
```

---

## 9. Tests — `tests/test_vocab_cli.py`

```python
"""Tests for vocabulary CLI commands."""

from unittest.mock import patch
from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()

# ... tests for vocab-seed command
```

---

## 10. Documentation Updates

- `docs/structure.md` — Add vocabulary tables and endpoints
- `README.md` — Add vocabulary section
- `AGENTS.md` — Update architecture section

---

## Execution Order

1. ✅ Models (`app/models.py`)
2. ✅ Seed data (`app/vocab_seed.py`)
3. ✅ CLI command (`app/cli.py`)
4. ✅ API schemas (`api/schemas.py`)
5. ✅ API endpoints (`api/main.py`)
6. ✅ Frontend screens + JS logic (`static/index.html`)
7. ✅ Dockerfile (no change needed)
8. ✅ Tests (`tests/test_vocab_api.py`, `tests/test_vocab_cli.py`)
9. ✅ Documentation updates
10. ✅ Run lint, typecheck, tests
