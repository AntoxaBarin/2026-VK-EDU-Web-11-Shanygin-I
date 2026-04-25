import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from questions.models import Answer, AnswerLike, Profile, Question, QuestionLike, Tag

fake = Faker()

BATCH_SIZE = 5000


class Command(BaseCommand):
    help = "Fill database with test data. Usage: python manage.py fill_db [ratio]"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, nargs="?", default=100)

    def handle(self, *args, **options):
        ratio = options["ratio"]
        self.stdout.write(f"Filling DB with ratio={ratio}...")

        users = self._create_users(ratio)
        self._create_profiles(users)
        tags = self._create_tags(ratio)
        questions = self._create_questions(ratio, users, tags)
        self._create_answers(ratio, questions, users)
        self._create_likes(ratio, users, questions)

        self.stdout.write(self.style.SUCCESS(f"Done! ratio={ratio}"))

    def _create_users(self, ratio):
        self.stdout.write("  Creating users...")
        existing = set(User.objects.values_list("username", flat=True))
        batch = []
        for _ in range(ratio):
            username = fake.unique.user_name()[:150]
            if username in existing:
                continue
            existing.add(username)
            batch.append(
                User(
                    username=username,
                    email=fake.email(),
                    first_name=fake.first_name()[:150],
                    last_name=fake.last_name()[:150],
                )
            )
            if len(batch) >= BATCH_SIZE:
                User.objects.bulk_create(batch, ignore_conflicts=True)
                batch = []
        if batch:
            User.objects.bulk_create(batch, ignore_conflicts=True)
        users = list(User.objects.all().only("id"))
        self.stdout.write(f"    total users: {len(users)}")
        return users

    def _create_profiles(self, users):
        self.stdout.write("  Creating profiles...")
        existing = set(Profile.objects.values_list("user_id", flat=True))
        batch = [Profile(user_id=u.id) for u in users if u.id not in existing]
        for i in range(0, len(batch), BATCH_SIZE):
            Profile.objects.bulk_create(
                batch[i : i + BATCH_SIZE], ignore_conflicts=True
            )

    def _create_tags(self, ratio):
        self.stdout.write("  Creating tags...")
        existing = set(Tag.objects.values_list("name", flat=True))
        batch = []
        for _ in range(ratio):
            name = fake.unique.word()[:64]
            if name in existing:
                continue
            existing.add(name)
            batch.append(Tag(name=name))
            if len(batch) >= BATCH_SIZE:
                Tag.objects.bulk_create(batch, ignore_conflicts=True)
                batch = []
        if batch:
            Tag.objects.bulk_create(batch, ignore_conflicts=True)
        tags = list(Tag.objects.all().only("id"))
        self.stdout.write(f"    total tags: {len(tags)}")
        return tags

    def _create_questions(self, ratio, users, tags):
        self.stdout.write("  Creating questions...")
        user_ids = [u.id for u in users]
        total = ratio * 10
        batch = []
        for _ in range(total):
            batch.append(
                Question(
                    title=fake.sentence(nb_words=8)[:255],
                    text=fake.paragraph(nb_sentences=5),
                    author_id=random.choice(user_ids),
                    votes=random.randint(-10, 500),
                )
            )
            if len(batch) >= BATCH_SIZE:
                Question.objects.bulk_create(batch)
                batch = []
        if batch:
            Question.objects.bulk_create(batch)

        questions = list(Question.objects.all().only("id"))

        self.stdout.write("  Assigning tags to questions...")
        tag_ids = [t.id for t in tags]
        through = Question.tags.through
        through_batch = []
        seen = set()
        for q in questions:
            chosen = random.sample(tag_ids, k=min(random.randint(1, 5), len(tag_ids)))
            for tid in chosen:
                key = (q.id, tid)
                if key not in seen:
                    seen.add(key)
                    through_batch.append(through(question_id=q.id, tag_id=tid))
            if len(through_batch) >= BATCH_SIZE:
                through.objects.bulk_create(through_batch, ignore_conflicts=True)
                through_batch = []
        if through_batch:
            through.objects.bulk_create(through_batch, ignore_conflicts=True)

        self.stdout.write(f"    total questions: {len(questions)}")
        return questions

    def _create_answers(self, ratio, questions, users):
        self.stdout.write("  Creating answers...")
        q_ids = [q.id for q in questions]
        u_ids = [u.id for u in users]
        total = ratio * 100
        batch = []
        for _ in range(total):
            batch.append(
                Answer(
                    question_id=random.choice(q_ids),
                    text=fake.paragraph(nb_sentences=3),
                    author_id=random.choice(u_ids),
                    is_correct=random.random() < 0.1,
                    votes=random.randint(-5, 100),
                )
            )
            if len(batch) >= BATCH_SIZE:
                Answer.objects.bulk_create(batch)
                batch = []
        if batch:
            Answer.objects.bulk_create(batch)
        self.stdout.write(f"    total answers: {ratio * 100}")

    def _create_likes(self, ratio, users, questions):
        self.stdout.write("  Creating likes...")
        u_ids = [u.id for u in users]
        q_ids = [q.id for q in questions]
        target = ratio * 100

        # QuestionLikes
        seen = set(QuestionLike.objects.values_list("user_id", "question_id"))
        batch = []
        attempts = 0
        while len(batch) < target and attempts < target * 5:
            attempts += 1
            uid = random.choice(u_ids)
            qid = random.choice(q_ids)
            if (uid, qid) not in seen:
                seen.add((uid, qid))
                batch.append(QuestionLike(user_id=uid, question_id=qid))
            if len(batch) >= BATCH_SIZE:
                QuestionLike.objects.bulk_create(batch, ignore_conflicts=True)
                batch = []
        if batch:
            QuestionLike.objects.bulk_create(batch, ignore_conflicts=True)

        # AnswerLikes
        answers = list(Answer.objects.all().only("id"))
        a_ids = [a.id for a in answers]
        seen = set(AnswerLike.objects.values_list("user_id", "answer_id"))
        batch = []
        attempts = 0
        while len(batch) < target and attempts < target * 5:
            attempts += 1
            uid = random.choice(u_ids)
            aid = random.choice(a_ids)
            if (uid, aid) not in seen:
                seen.add((uid, aid))
                batch.append(AnswerLike(user_id=uid, answer_id=aid))
            if len(batch) >= BATCH_SIZE:
                AnswerLike.objects.bulk_create(batch, ignore_conflicts=True)
                batch = []
        if batch:
            AnswerLike.objects.bulk_create(batch, ignore_conflicts=True)

        self.stdout.write(f"    target likes per type: {target}")
