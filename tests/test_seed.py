"""Tests for the seed_verbs function."""

from app.models import Verb
from app.seed import seed_verbs

# Sample verb tuples matching seed.py format: (base, past, participle, past_alt, participle_alt, meaning)
SAMPLE_VERBS = [
    ("go", "went", "gone", None, None, "ir"),
    ("read", "read", "read", None, None, "leer"),
    ("learn", "learned", "learned", "learnt", "learnt", "aprender"),
]


class TestSeedVerbs:
    def test_seed_inserts_new_verbs(self, db):
        added, updated = seed_verbs(db, verb_list=SAMPLE_VERBS)
        assert added == 3
        assert updated == 0
        count = db.query(Verb).count()
        assert count == 3

    def test_seed_updates_existing_verbs(self, db):
        # First seed
        seed_verbs(db, verb_list=SAMPLE_VERBS)

        # Second seed — should update, not insert
        added, updated = seed_verbs(db, verb_list=SAMPLE_VERBS)
        assert added == 0
        assert updated == 3
        count = db.query(Verb).count()
        assert count == 3

    def test_seed_partial_update(self, db):
        # Seed first batch
        seed_verbs(db, verb_list=SAMPLE_VERBS[:1])

        # Seed full batch — should add 2, update 1
        added, updated = seed_verbs(db, verb_list=SAMPLE_VERBS)
        assert added == 2
        assert updated == 1
        count = db.query(Verb).count()
        assert count == 3

    def test_seed_stores_verb_data_correctly(self, db):
        seed_verbs(db, verb_list=SAMPLE_VERBS)
        verb = db.query(Verb).filter(Verb.base == "learn").first()
        assert verb is not None
        assert verb.past == "learned"
        assert verb.participle == "learned"
        assert verb.past_alt == "learnt"
        assert verb.participle_alt == "learnt"
        assert verb.meaning == "aprender"

    def test_seed_empty_list(self, db):
        added, updated = seed_verbs(db, verb_list=[])
        assert added == 0
        assert updated == 0

    def test_seed_with_alt_forms_none(self, db):
        """Verbs with None alt forms should be stored as None."""
        seed_verbs(db, verb_list=SAMPLE_VERBS)
        verb = db.query(Verb).filter(Verb.base == "go").first()
        assert verb.past_alt is None
        assert verb.participle_alt is None
