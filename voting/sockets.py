import json

from channels import Group
from channels.sessions import channel_session
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

from voting.models import Meeting, MadeVote, Attendant, Scanner
from voting.serializers import VoteDetailsSerializer, AttendantSerializer, SimpleScannerSerializer


@channel_session
def ws_connect(message):
    """
    Called when a client attempts to connect using websockets. The path must
    be on the format '/meeting/%d/?token=%s'. Connecting will subscribe the
    client to updates to meeting votes.
    """

    path = message['path']
    if path.startswith('/meeting/'):
        meeting_id = path.split('/')[2]

        try:
            meeting = Meeting.objects.get(pk=meeting_id)
            meeting_id = str(meeting.id)  # Filter value to ensure it has consistent format
        except Meeting.DoesNotExist:
            # This error message gives information of which meetings does or does not exist,
            # as it is sent before authenticating the user. We ignore this security flaw as
            # we do not considered meeting ids to be sensitive information.
            reject(message, 'Meeting does not exist')
            return

        user = user_from_token(message)
        if has_sufficient_privileges(user, meeting):
            # Subscribe websocket to update channel
            Group('meeting-' + meeting_id).add(message.reply_channel)
            message.channel_session['meeting'] = meeting_id

            # Accept the connection
            message.reply_channel.send({"accept": True})
        else:
            reject(message, 'Not permitted')
    else:
        reject(message, 'Unrecognized path requested')


@receiver(post_save, sender=MadeVote)
def vote_was_made(sender, instance, created, **kwargs):
    """
    We subscribe to the signals Django emit when a model has been saved and
    forward them to our subscribed clients.

    Reason: A MadeVote instance was (saved) created.
    """

    if created:
        response = {
            'type': 'vote_details',
            'data': VoteDetailsSerializer(instance.vote).data
        }
        Group('meeting-' + str(instance.vote.meeting.id)).send({'text': json.dumps(response)})


@receiver(post_save, sender=Attendant)
@receiver(post_delete, sender=Attendant)
def attendants_list_changed(sender, instance, *args, **kwargs):
    """
    We subscribe to the signals Django emit when a model has been saved and
    forward them to our subscribed clients.

    Reason: An Attendant instance was (saved) created or deleted.
    """

    response = {
        'type': 'attendants_list',
        'data': AttendantSerializer(instance.meeting.attendant_set, many=True).data
    }
    Group('meeting-' + str(instance.meeting.id)).send({'text': json.dumps(response)})


@receiver(post_save, sender=Scanner)
@receiver(post_delete, sender=Scanner)
def scanner_list_changed(sender, instance, *args, **kwargs):
    """
    We subscribe to the signals Django emit when a model has been saved and
    forward them to our subscribed clients.

    Reason: A Scanner instance was (saved) created or deleted.
    """

    response = {
        'type': 'scanner_list',
        'data': SimpleScannerSerializer(instance.meeting.scanner_set, many=True).data
    }
    Group('meeting-' + str(instance.meeting.id)).send({'text': json.dumps(response)})


@channel_session
def ws_disconnect(message):
    """
    Called when a client is disconnected. We unsubscribe the client from
    further updates to the meeting it was previously subscribed to.
    """

    meeting_id = message.channel_session.get('meeting')
    if meeting_id is not None:
        Group('meeting-' + meeting_id).discard(message.reply_channel)


def reject(message, reason):
    response = {
        'type': 'error',
        'data': reason
    }

    message.reply_channel.send({"text": json.dumps(response)})
    message.reply_channel.send({"close": True})


def has_sufficient_privileges(user, meeting):
    return meeting.section.is_admin(user)


def user_from_token(message):
    query_string = message['query_string']
    if isinstance(query_string, str):
        path = query_string
    else:
        path = query_string.decode('utf-8')

    key = 'token='
    if key in path:
        token = path[path.index(key) + len(key):]

        try:
            data = VerifyJSONWebTokenSerializer().validate({'token': token})
            return data['user']
        except ValidationError:
            return None

    return None


channel_routing = {
    'websocket.connect': ws_connect,
    'websocket.disconnect': ws_disconnect,
}
