import os

import boto3
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from kagiso_auth.models import KagisoUser

import mistune
from mptt.models import TreeForeignKey
from PIL import Image

from radio_community.utils.model_utils import (
    ContentTypeAware,
    MttpContentTypeAware
)

s3_resource = boto3.resource(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


def validate_image(field_file_obj):
    file_size = field_file_obj.file.size
    megabyte_limit = 10.0
    if file_size > megabyte_limit * 1024 * 1024:
        raise ValidationError(
            'Max file size is {0}MB'.format(megabyte_limit)
        )
    if field_file_obj.width > settings.MIN_IMAGE_WIDTH or field_file_obj.height > settings.MIN_IMAGE_HEIGHT:  # noqa
        raise ValidationError(
            'Maximum WIDTH: {0} & HEIGHT: {1}.'.format(
                settings.MIN_IMAGE_WIDTH,
                settings.MIN_IMAGE_HEIGHT
            )
        )
    field_file_obj.file.seek(0)
    if field_file_obj.file.content_type not in (
            'image/png', 'image/jpeg', 'image/gif'
    ):
        raise ValidationError(
            'Image is not valid. Please upload a JPEG, PNG or GIF image.'
        )


class CustomUser(models.Model):
    user = models.ForeignKey(KagisoUser, on_delete=models.PROTECT)
    moderator = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Submission(ContentTypeAware):
    author_name = models.CharField(null=False, max_length=50)
    author = models.ForeignKey(
        'kagiso_auth.KagisoUser',
        on_delete=models.CASCADE,
        related_name='+'
    )
    title = models.CharField(max_length=250)
    url = models.URLField(null=True, blank=True)
    image = models.ImageField(
        upload_to='images/radio_com/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[validate_image]
    )
    image_url = models.CharField(
        blank=True,
        max_length=5000
    )
    image_compress_url = models.CharField(
        blank=True,
        max_length=5000
    )
    text = models.TextField(max_length=5000, blank=True)
    text_html = models.TextField(blank=True)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    comment_count = models.IntegerField(default=0)
    is_moderated = models.BooleanField(default=False)
    is_under_review = models.BooleanField(default=False)

    def generate_html(self):
        if self.text:
            html = mistune.markdown(self.text)
            self.text_html = html

    @property
    def linked_url(self):
        if self.url:
            return '{}'.format(self.url)
        else:
            return '/comments/{}'.format(self.id)

    @property
    def comments_url(self):
        return '/comments/{}'.format(self.id)

    def __unicode__(self):
        return '<Submission:{}>'.format(self.id)

    def up_load_to_s3_after_compress(self):
        try:
            local_file_name = str(self.image.name).split('/').pop()
            compressed_key = 'compressed/{0}'.format(self.image.name)
            my_bucket = settings.AWS_STORAGE_BUCKET_NAME
            data = open(local_file_name, 'r+b')
            data.seek(0)
            s3_resource_bucket = s3_resource.Bucket(my_bucket)
            s3_resource_bucket.put_object(
                Key=compressed_key,
                Body=data,
                ContentType='image/jpeg'
            )
            data.close()
        except FileNotFoundError:
            pass

    def __str__(self):
        return self.title


class Comment(MttpContentTypeAware):
    author_name = models.CharField(null=False, max_length=50)
    author = models.ForeignKey(
        'kagiso_auth.KagisoUser',
        on_delete=models.CASCADE,
        related_name='+'
    )
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    parent = TreeForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(default=timezone.now)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    raw_comment = models.TextField(blank=True)
    html_comment = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='images/radio_com/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[validate_image]
    )
    image_url = models.CharField(
        blank=True,
        max_length=5000
    )
    image_compress_url = models.CharField(
        blank=True,
        max_length=5000
    )

    class MPTTMeta:
        order_insertion_by = ['-score']

    @classmethod
    def create(cls, author, raw_comment, parent):
        """
        Create a new comment instance. If the parent is submisison
        update comment_count field and save it.
        If parent is comment post it as child comment
        :param author: RedditUser instance
        :type author: RedditUser
        :param raw_comment: Raw comment text
        :type raw_comment: str
        :param parent: Comment or Submission that this comment is child of
        :type parent: Comment | Submission
        :return: New Comment instance
        :rtype: Comment
        """

        html_comment = mistune.markdown(raw_comment)
        # todo: any exceptions possible?
        comment = cls(author=author,
                      author_name=author.username,
                      raw_comment=raw_comment,
                      html_comment=html_comment)

        if isinstance(parent, Submission):
            submission = parent
            comment.submission = submission
        elif isinstance(parent, Comment):
            submission = parent.submission
            comment.submission = submission
            comment.parent = parent
        else:
            return
        submission.comment_count += 1
        submission.save()

        return comment

    def __unicode__(self):
        return '<Comment:{}>'.format(self.id)


class Vote(models.Model):
    user = models.ForeignKey(
        'kagiso_auth.KagisoUser',
        on_delete=models.CASCADE,
        related_name='+'
    )
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    vote_object_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    vote_object_id = models.PositiveIntegerField()
    vote_object = GenericForeignKey('vote_object_type', 'vote_object_id')
    value = models.IntegerField(default=0)

    @classmethod
    def create(cls, user, vote_object, vote_value):
        """
        Create a new vote object and return it.
        It will also update the ups/downs/score fields in the
        vote_object instance and save it.

        :param user: RedditUser instance
        :type user: RedditUser
        :param vote_object: Instance of the object the vote is cast on
        :type vote_object: Comment | Submission
        :param vote_value: Value of the vote
        :type vote_value: int
        :return: new Vote instance
        :rtype: Vote
        """

        if isinstance(vote_object, Submission):
            submission = vote_object
            # vote_object.author.link_karma += vote_value
        else:
            submission = vote_object.submission
            # vote_object.author.comment_karma += vote_value

        vote = cls(user=user,
                   vote_object=vote_object,
                   value=vote_value)

        vote.submission = submission
        # the value for new vote will never be 0
        # that can happen only when removing up/down vote.
        vote_object.score += vote_value
        if vote_value == 1:
            vote_object.ups += 1
        elif vote_value == -1:
            vote_object.downs += 1

        vote_object.save()
        vote_object.author.save()

        return vote

    def change_vote(self, new_vote_value):
        if self.value == -1 and new_vote_value == 1:  # down to up
            vote_diff = 2
            self.vote_object.score += 2
            self.vote_object.ups += 1
            self.vote_object.downs -= 1
        elif self.value == 1 and new_vote_value == -1:  # up to down
            vote_diff = -2
            self.vote_object.score -= 2
            self.vote_object.ups -= 1
            self.vote_object.downs += 1
        elif self.value == 0 and new_vote_value == 1:  # canceled vote to up
            vote_diff = 1
            self.vote_object.ups += 1
            self.vote_object.score += 1
        elif self.value == 0 and new_vote_value == -1:  # canceled vote to down
            vote_diff = -1
            self.vote_object.downs += 1
            self.vote_object.score -= 1
        else:
            return None

        if isinstance(self.vote_object, Submission):
            pass
            # self.vote_object.author.link_karma += vote_diff
        else:
            pass
            # self.vote_object.author.comment_karma += vote_diff

        self.value = new_vote_value
        self.vote_object.save()
        self.vote_object.author.save()
        self.save()

        return vote_diff

    def cancel_vote(self):
        if self.value == 1:
            vote_diff = -1
            self.vote_object.ups -= 1
            self.vote_object.score -= 1
        elif self.value == -1:
            vote_diff = 1
            self.vote_object.downs -= 1
            self.vote_object.score += 1
        else:
            return None

        if isinstance(self.vote_object, Submission):
            pass
            # self.vote_object.author.link_karma += vote_diff
        else:
            pass
            # self.vote_object.author.comment_karma += vote_diff

        self.value = 0
        self.save()
        self.vote_object.save()
        self.vote_object.author.save()
        return vote_diff


class ReportSubmission(models.Model):
    reported_by = models.ForeignKey(KagisoUser, on_delete=models.PROTECT)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.submission.title


def create_image_url(instance):
    if not instance.image_url:
        s3_domain = 's3.amazonaws.com'
        s3_key = instance.image.file.obj.key
        s3_bucket_name = instance.image.file.obj.bucket_name
        s3_full_file_url = 'https://{0}.{1}/{2}'.format(
            s3_bucket_name, s3_domain, s3_key
        )
        instance.image_url = s3_full_file_url
        instance.save()


def compress_image(instance):
    image_url = instance.image_url
    original_image = 'original_image.jpg'
    compressed_image = 'compressed_image.jpg'

    if 'compressed' in str(image_url):
        return None, None, None

    key = ''
    if image_url:
        picture_key = str(image_url).split('images')
        key = 'images{0}'.format(picture_key[1])
        s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME).download_file(
            key, original_image
        )
    try:
        image = Image.open(original_image)
        rgb_image = image.convert('RGB')
        rgb_image.save(compressed_image, format='JPEG', qaulity=80)
        rgb_image.close()
    except FileNotFoundError:
        pass

    if not key:
        return None, None, None

    compressed_key = 'compressed/{0}'.format(key)
    try:
        local_file_name = compressed_image
        my_bucket = settings.AWS_STORAGE_BUCKET_NAME
        data = open(local_file_name, 'r+b')
        data.seek(0)
        s3_resource_bucket = s3_resource.Bucket(my_bucket)
        s3_resource_bucket.put_object(
            Key=compressed_key,
            Body=data,
            ContentType='image/jpeg'
        )
        data.close()
    except FileNotFoundError:
        pass

    s3_full_file_url = '{0}{1}'.format(picture_key[0], compressed_key)
    return s3_full_file_url, original_image, compressed_image


def delete_local_images(compressed_image, original_image):
    if original_image:
        try:
            os.remove(original_image) if os.path.exists(
                original_image) else None
        except FileNotFoundError:
            pass
    if compressed_image:
        try:
            os.remove(compressed_image) if os.path.exists(
                compressed_image) else None
        except FileNotFoundError:
            pass


@receiver(post_save, sender=Submission)
def update_picture_file_url_submission(sender, instance, **kwargs):
    if instance.image:
        create_image_url(instance)
        compress_url, original_image, compressed_image = compress_image(instance)   # noqa
        if not instance.image_compress_url:
            instance.image_compress_url = compress_url
            instance.save()
        delete_local_images(compressed_image, original_image)


@receiver(post_save, sender=Comment)
def update_picture_file_url_comment(sender, instance, **kwargs):
    if instance.image:
        create_image_url(instance)
        compress_url, original_image, compressed_image = compress_image(instance)   # noqa
        if not instance.image_compress_url:
            instance.image_compress_url = compress_url
            instance.save()
        delete_local_images(compressed_image, original_image)


def get_filtered_submissions():
    return Submission \
        .objects \
        .order_by('-score') \
        .all() \
        .exclude(is_under_review=True) \
        .exclude(is_moderated=False)


def get_unfiltered_submissions():
    return Submission \
        .objects \
        .order_by('-score') \
        .all() \
        .exclude(is_under_review=True) \
        .exclude(is_moderated=True)
