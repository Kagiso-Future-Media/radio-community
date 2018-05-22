from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register
from kagiso_auth.models import KagisoUser

from reddit.forms import SubmissionForm
from reddit.models import (
    Comment,
    CustomUser,
    get_filtered_submissions,
    get_unfiltered_submissions,
    ReportSubmission,
    Submission,
    Vote
)
from reddit.utils.helpers import post_only


@register.filter
def get_item(dictionary, key):  # pragma: no cover
    """
    Needed because there's no built in .get in django templates
    when working with dictionaries.

    :param dictionary: python dictionary
    :param key: valid dictionary key type
    :return: value of that key or None
    """
    return dictionary.get(key)


def raw_page(request):
    """
    Serves raw submission listings
    """
    raw_submissions = get_unfiltered_submissions()
    submissions, submission_votes, is_user_admin = page_body(request, raw_submissions)   # noqa

    return render(
        request,
        'public/raw.html',
        {
            'submissions': submissions,
            'submission_votes': submission_votes,
            'current_user': request.user
        }
    )


def review_page(request):
    """
    Serves review listings. ADMINS ONLY!
    """

    review_submissions = Submission \
        .objects \
        .order_by('-score') \
        .exclude(is_under_review=False)
    submissions, submission_votes, is_user_admin = page_body(request, review_submissions)    # noqa
    if not is_user_admin:
        return HttpResponseForbidden()
    return render(
        request,
        'public/review.html',
        {
            'submissions': submissions,
            'submission_votes': submission_votes,
            'is_user_admin': is_user_admin,
        }
    )


def home_page(request):
    """
    Serves frontpage and all additional submission listings
    with maximum of 25 submissions per page.
    """
    # TODO: Serve user votes on submissions too.

    all_submissions = get_filtered_submissions()
    _raw_submissions = get_unfiltered_submissions()
    submissions, submission_votes, is_user_admin = page_body(request, all_submissions)   # noqa
    raw_submissions, submission_votes, is_user_admin = page_body(request, _raw_submissions)   # noqa
    reported_posts = Submission.objects.filter(is_under_review=True).count()

    return render(
        request,
        'public/frontpage.html',
        {
            'submissions': submissions,
            'raw_submissions': raw_submissions,
            'submission_votes': submission_votes,
            'is_user_admin': is_user_admin,
            'current_user': request.user,
            'reported_posts': reported_posts,
            'raw_post_count': _raw_submissions.count
        }
    )


def comments(request, thread_id=None):
    """
    Handles comment view when user opens the thread.
    On top of serving all comments in the thread it will
    also return all votes user made in that thread
    so that we can easily update comments in template
    and display via css whether user voted or not.

    :param thread_id: Thread ID as it's stored in database
    :type thread_id: int
    """

    this_submission = get_object_or_404(Submission, id=thread_id)

    thread_comments = Comment.objects.filter(submission=this_submission)

    is_user_admin = False
    if request.user.is_authenticated:
        is_user_admin = CustomUser.objects.filter(
            user=request.user,
            admin=True
        )

    if request.user.is_authenticated:
        try:
            reddit_user = KagisoUser.objects.get(id=request.user.id)
        except KagisoUser.DoesNotExist:
            reddit_user = None
    else:
        reddit_user = None

    sub_vote_value = None
    comment_votes = {}

    if reddit_user:

        try:
            vote = Vote.objects.get(
                vote_object_type=this_submission.get_content_type(),
                vote_object_id=this_submission.id,
                user=reddit_user)
            sub_vote_value = vote.value
        except Vote.DoesNotExist:
            pass

        try:
            user_thread_votes = Vote.objects.filter(
                id=reddit_user.id,
                submission=this_submission
            )

            for vote in user_thread_votes:
                comment_votes[vote.vote_object.id] = vote.value
        except:  # noqa
            pass

    return render(
        request,
        'public/comments.html',
        {
            'submission': this_submission,
            'comments': thread_comments,
            'comment_votes': comment_votes,
            'sub_vote': sub_vote_value,
            'current_user': request.user,
            'is_user_admin': is_user_admin
        }
    )


@post_only
def post_comment(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'msg': 'You need to log in to post new comments.'})

    parent_type = request.POST.get('parentType', None)
    parent_id = request.POST.get('parentId', None)
    raw_comment = request.POST.get('commentContent', None)

    if not all([parent_id, parent_type]) or \
                    parent_type not in ['comment', 'submission'] or \
            not parent_id.isdigit():  # noqa
        return HttpResponseBadRequest()

    if not raw_comment:
        return JsonResponse({'msg': 'You have to write something.'})
    author = KagisoUser.objects.get(id=request.user.id)
    parent_object = None
    try:  # try and get comment or submission we're voting on
        if parent_type == 'comment':
            parent_object = Comment.objects.get(id=parent_id)
        elif parent_type == 'submission':
            parent_object = Submission.objects.get(id=parent_id)

    except (Comment.DoesNotExist, Submission.DoesNotExist):
        return HttpResponseBadRequest()

    comment = Comment.create(author=author,
                             raw_comment=raw_comment,
                             parent=parent_object)

    comment.save()
    return JsonResponse({'msg': 'Your comment has been posted.'})


@post_only
def vote(request):

    # The type of object we're voting on, can be 'submission' or 'comment'
    vote_object_type = request.POST.get('what', None)

    # The ID of that object as it's stored in the database, positive int
    vote_object_id = request.POST.get('what_id', None)

    # The value of the vote we're writing to that object, -1 or 1
    # Passing the same value twice will cancel the vote i.e. set it to 0
    new_vote_value = request.POST.get('vote_value', None)

    # By how much we'll change the score, used to modify score on the fly
    # client side by the javascript instead of waiting for a refresh.
    vote_diff = 0

    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    else:
        user = KagisoUser.objects.get(id=request.user.id)

    try:  # If the vote value isn't an integer that's equal to -1 or 1
        # the request is bad and we can not continue.
        new_vote_value = int(new_vote_value)
        if new_vote_value not in [-1, 1]:
            raise ValueError('Wrong value for the vote!')

    except (ValueError, TypeError):
        return HttpResponseBadRequest()
    # if one of the objects is None, 0 or some other bool(value) == False value
    # or if the object type isn't 'comment' or 'submission' it's a bad request
    if not all([vote_object_type, vote_object_id, new_vote_value]) or \
                    vote_object_type not in ['comment', 'submission']:  # noqa
        return HttpResponseBadRequest()

    # Try and get the actual object we're voting on.
    try:
        if vote_object_type == 'comment':
            vote_object = Comment.objects.get(id=vote_object_id)

        elif vote_object_type == 'submission':
            vote_object = Submission.objects.get(id=vote_object_id)
        else:
            return HttpResponseBadRequest()  # should never happen

    except (Comment.DoesNotExist, Submission.DoesNotExist):
        return HttpResponseBadRequest()

    # Try and get the existing vote for this object, if it exists.
    try:
        vote = Vote.objects.get(
            vote_object_type=vote_object.get_content_type(),
            vote_object_id=vote_object.id,
            user=user)

    except Vote.DoesNotExist:
        # Create a new vote and that's it.
        vote = Vote.create(user=user,
                           vote_object=vote_object,
                           vote_value=new_vote_value)
        vote.save()
        vote_diff = new_vote_value

    if vote_object_type == 'submission':
        submission = get_object_or_404(Submission, id=vote_object_id)

        if submission.score > 9 and submission.is_moderated is False:
            submission.is_moderated = True
            submission.save()

        return JsonResponse({'error': None,
                             'voteDiff': vote_diff})

    # User already voted on this item, this means the vote is either
    # being canceled (same value) or changed (different new_vote_value)
    if vote.value == new_vote_value:
        # canceling vote
        vote_diff = vote.cancel_vote()
        if not vote_diff:
            return HttpResponseBadRequest(
                'Something went wrong while canceling the vote')
    else:
        # changing vote
        vote_diff = vote.change_vote(new_vote_value)
        if not vote_diff:
            return HttpResponseBadRequest(
                'Wrong values for old/new vote combination')

    return JsonResponse({'error': None,
                         'voteDiff': vote_diff})


@login_required
def submit(request):
    """
    Handles new submission.. submission.
    """
    submission_form = SubmissionForm()

    if request.method == 'POST':
        submission_form = SubmissionForm(request.POST, request.FILES)
        if submission_form.is_valid():
            submission = submission_form.save(commit=False)
            submission.generate_html()
            reddit_user = KagisoUser.objects.get(id=request.user.id)
            submission.author = reddit_user
            submission.author_name = '{} {}'.format(
                reddit_user.first_name,
                reddit_user.last_name
            )
            submission.save()
            messages.success(request, 'Submission created')
            return redirect('/')

    return render(request, 'public/submit.html', {'form': submission_form})


def delete_submission(request, object_id):
    submission = get_object_or_404(Submission, pk=object_id)
    title = submission.title
    submission.delete()
    messages.success(
        request, 'Submission "{}" has been deleted successfully.'.format(title)
    )
    return redirect('/')


def delete_comment(request, object_id):
    node = get_object_or_404(Comment, pk=object_id)
    title = node.title
    node.delete()
    messages.success(
        request, 'Comment {} has been deleted successfully.'.format(title)
    )
    return redirect('/')


@login_required
def promote_submission(request, object_id):
    submission = get_object_or_404(Submission, pk=object_id)
    submission.is_under_review = False
    submission.moderated = False
    submission.save()
    messages.success(
        request,
        'Submission "{0}" has been promoted.'.format(submission.title)
    )
    return redirect('/')


def report_submission(request, object_id):
    if not request.user.is_authenticated:
        messages.warning(
            request, 'You need to be logged in to report a post.'
        )
        return redirect('/sign_in/?next={}'.format(request.path))
    else:
        submission = get_object_or_404(Submission, pk=object_id)
        if ReportSubmission.objects.filter(
                reported_by=request.user,
                submission=submission
        ).exists():
            messages.warning(
                request, 'This post has been reported.'.format(object_id)
            )
            return redirect('/')
        report = ReportSubmission()
        report.reported_by = request.user
        report.submission = submission
        report.save()
        report_count = ReportSubmission.objects.filter(
            submission=submission
        ).count()
        if report_count > 9:
            submission.is_under_review = True
            submission.save()
        messages.success(
            request,
            'Submission by "{0} {1}" has been reported'.format(
                submission.author.first_name,
                submission.author.last_name
            )
        )
        return redirect('/')


def page_body(request, submissions):
    paginator = Paginator(submissions, 25)

    page = request.GET.get('page', 1)
    try:
        submissions = paginator.page(page)
    except PageNotAnInteger:
        raise Http404
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)

    submission_votes = {}

    is_user_admin = False
    if request.user.is_authenticated:
        is_user_admin = CustomUser.objects.filter(
            user=request.user,
            admin=True
        )
        for submission in submissions:
            try:
                vote = Vote.objects.get(
                    vote_object_type=submission.get_content_type(),
                    vote_object_id=submission.id,
                    user=KagisoUser.objects.get(id=request.user.id))
                submission_votes[submission.id] = vote.value
            except Vote.DoesNotExist:
                pass
    return submissions, submission_votes, is_user_admin
