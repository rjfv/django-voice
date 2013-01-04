from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import pgettext
from django.utils.translation import ugettext_lazy as _
from qhonuskan_votes.models import VotesField
from qhonuskan_votes.models import ObjectsWithScoresManager

STATUS_CHOICES = (
    ('open', pgettext('status', "Open")),
    ('closed', pgettext('status', "Closed")),
)


class Status(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500)
    default = models.BooleanField(
        blank=True,
        help_text=_("New feedback will have this status"))
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    def save(self, **kwargs):
        if self.default:
            try:
                default_project = Status.objects.get(default=True)
                default_project.default = False
                default_project.save()

            except Status.DoesNotExist:
                pass

        super(Status, self).save(**kwargs)

    def __unicode__(self):
        return unicode(self.title)

    class Meta:
        verbose_name = _("status")
        verbose_name_plural = _("statuses")


class Type(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500)

    def __unicode__(self):
        return self.title


class Feedback(models.Model):
    type = models.ForeignKey(Type, verbose_name=_("Type"))
    title = models.CharField(max_length=500, verbose_name=_("Title"))
    description = models.TextField(
        blank=True, verbose_name=_("Description"),
        help_text=_(
            "This will be viewable by other people - do not include any "
            "private details such as passwords or phone numbers here."))
    anonymous = models.BooleanField(
        blank=True, verbose_name=_("Anonymous"),
        help_text=_("Do not show who sent this"))
    private = models.BooleanField(
        verbose_name=_("Private"), blank=True,
        help_text=_(
            "Hide from public pages. Only site administrators will be able to "
            "view and respond to this"))
    user = models.ForeignKey(
        User, blank=True, null=True, verbose_name=_("User"))
    email = models.EmailField(
        blank=True, null=True, verbose_name=_('E-mail'),
        help_text=_(
            "You must provide your e-mail so we can answer to you. "
            "Alternatively you can bookmark next page and check out for an "
            "answer later."))
    slug = models.SlugField(max_length=10, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.ForeignKey(Status, verbose_name=_('Status'))
    duplicate = models.ForeignKey(
        'self', null=True, blank=True, verbose_name=_("Duplicate"))
    votes = VotesField()
    objects = ObjectsWithScoresManager()

    def save(self, **kwargs):
        try:
            self.status

        except Status.DoesNotExist:
            try:
                default = Status.objects.get(default=True)

            except Status.DoesNotExist:
                default = Status.objects.all()[0]

            self.status = default

        super(Feedback, self).save(**kwargs)

    @models.permalink
    def get_absolute_url(self):
        return 'djangovoice_item', (self.id,)

    def __unicode__(self):
        return unicode(self.title)

    class Meta:
        verbose_name = _("feedback")
        verbose_name_plural = _("feedback")
        ordering = ('-created',)
        get_latest_by = 'created'
