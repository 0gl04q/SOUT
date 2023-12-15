from django.db.models.signals import pre_delete
from django.dispatch import receiver
from verification_app.models import WorkPlace, FileSOUT
from django.db import transaction
from django.db.models import Count, Q


@receiver(pre_delete, sender=FileSOUT)
def handle_pre_delete(sender, instance, **kwargs):
    wp_file = WorkPlace.objects.filter(file=instance).values('place_id')

    wp_repeat = WorkPlace.objects.filter(
        status=WorkPlace.WARNING,
        organization=instance.organization
    ).values("place_id").annotate(
        count_wp=Count("place_id")
    ).values("place_id").filter(count_wp=2, place_id__in=wp_file)

    files = FileSOUT.objects.filter(
        organization=instance.organization,
        date__lt=instance.date
    )

    wp_itg = WorkPlace.objects.filter(file__in=files, place_id__in=wp_repeat)

    with transaction.atomic():
        for work_place in wp_itg:
            work_place.status = WorkPlace.CHECKED
            work_place.save()
