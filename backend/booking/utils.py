from .models import Booking, ItemPoolAccessory, ItemPoolItem
from rest_framework import serializers


def should_auto_confirm(data, instance):
    # If item pool requires confirmation, do not auto confirm.
    if data["pool"].requires_confirmation:
        return False

    # If booking is a normal booking.
    if not data["restricted_timeslot"]:
        queryset = Booking.objects.all()  # type: ignore[attr-defined]

        # on update don't compare with self.
        if instance:
            queryset = queryset.exclude(pk=instance.id)

        # If no confirmed restricted timeslot is overlapping with booking, auto confirm.
        queryset = queryset.filter(  # type: ignore[attr-defined]
            pool=data["pool"],
            restricted_timeslot=True,
            confirmed=True,
            start__lte=data["end"],
            end__gte=data["start"],
        )
        return not queryset.exists()

    # Restricted timeslot bookings should not be auto-confirmed by default.
    return False


def assign_items_and_accessories(
    instance, start, end, pool, count, restricted_timeslot
):
    # collect items with available accessories, choosing those with
    # highest priority first
    all_items = (
        ItemPoolItem.objects.filter(pool=pool, enabled=True).order_by("-priority").all()
    )

    overlap_query = get_overlap_query(start, end, pool, restricted_timeslot, instance)

    items = []
    accessories = []

    for item in all_items:
        item_overlap_query = overlap_query.filter(items__in=[item])

        if item_overlap_query.exists():
            continue

        if pool.requires_accessory:
            compat_accessories = (
                ItemPoolAccessory.objects.filter(pool=pool)
                .filter(compatible_items=item)
                .all()
            )

            # find the first accessory (if any) that is not already assigned
            for accessory in compat_accessories:
                if accessory in accessories:
                    continue

                # check overlap for accessory as well
                accessory_overlap_query = overlap_query.filter(
                    accessories__in=[accessory]
                )
                if accessory_overlap_query.exists():
                    continue
                accessories.append(accessory)
                items.append(item)
                break
        else:
            items.append(item)

        if len(items) >= count:
            # we're done!
            break

    if len(items) < count:
        raise serializers.ValidationError(
            f"Not enough available items or accessories available to satisfy the booking: {len(items)} available sets found."
        )

    return items, accessories


def get_overlap_query(start, end, pool, restricted_timeslot, instance=None):
    queryset = Booking.objects.filter(
        pool=pool, restricted_timeslot=restricted_timeslot
    )
    if instance:
        queryset = queryset.exclude(pk=instance.id)

    return queryset.filter(start__lte=end, end__gte=start)


def check_overlap(booking, items, accessories):
    overlap_query = get_overlap_query(
        booking.start, booking.end, booking.pool, booking.restricted_timeslot, booking
    )

    if items:
        item_overlap_query = overlap_query.filter(items__in=items)
        if item_overlap_query.exists():
            return True

    if accessories:
        accessory_overlap_query = overlap_query.filter(accessories__in=accessories)
        if accessory_overlap_query.exists():
            return True

    return False
