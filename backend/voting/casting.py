"""Read and protect vote eligibility for the lifetime of the caller's transaction.

Keep choice reads separate from voter reads: no SQL statement contains both a
voter identifier and an alternative identifier. PostgreSQL SHARE locks allow
parallel voters while blocking edits/deletion of the validated state.
"""

from dataclasses import dataclass
from uuid import uuid4

from django.db import IntegrityError, connection, transaction

from backend.membership.models import Member
from .models import Alternative, Attendant, MadeVote


@dataclass(frozen=True, slots=True)
class Choice:
    id: int
    text: str
    vote_id: int
    open: bool
    meeting_id: int
    current_vote_id: int | None


def lock_choice(alternative_id):
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT a.id, a.text, v.id, v.open, v.meeting_id, m.current_vote_id
                FROM voting_alternative a
                JOIN voting_vote v ON v.id = a.vote_id
                JOIN voting_meeting m ON m.eventbase_ptr_id = v.meeting_id
                WHERE a.id = %s
                FOR SHARE OF v, m
                """,
                [alternative_id],
            )
            row = cursor.fetchone()
        if row is None:
            raise Alternative.DoesNotExist
        return Choice(*row)

    # SQLite is supported for single-threaded application tests. Concurrent
    # voting guarantees are verified against the deployment database, PostgreSQL.
    alternative = Alternative.objects.select_related("vote__meeting").get(
        pk=alternative_id
    )
    vote = alternative.vote
    return Choice(
        alternative.pk,
        alternative.text,
        vote.pk,
        vote.open,
        vote.meeting_id,
        vote.meeting.current_vote_id,
    )


def lock_eligibility(meeting_id, user):
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT a.id
                FROM voting_attendant a
                JOIN membership_member m ON m.liu_id = %s
                WHERE a.meeting_id = %s AND a.user_id = %s
                  AND a.has_voting_rights AND m.membership_type = 'S'
                FOR SHARE OF a, m
                """,
                [user.username, meeting_id, user.pk],
            )
            return cursor.fetchone() is not None

    return (
        Attendant.objects.filter(
            meeting_id=meeting_id, user=user, has_voting_rights=True
        ).exists()
        and Member.objects.filter(liu_id=user.username, membership_type="S").exists()
    )


def claim_vote(user_id, vote_id):
    """Claim participation once, without ever accepting a choice identifier."""
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO voting_madevote (id, user_id, vote_id) VALUES (%s, %s, %s)
                ON CONFLICT ON CONSTRAINT one_vote_per_user DO NOTHING
                RETURNING id
                """,
                [uuid4(), user_id, vote_id],
            )
            return cursor.fetchone() is not None

    try:
        with transaction.atomic():
            MadeVote.objects.create(user_id=user_id, vote_id=vote_id)
        return True
    except IntegrityError:
        if MadeVote.objects.filter(user_id=user_id, vote_id=vote_id).exists():
            return False
        raise
