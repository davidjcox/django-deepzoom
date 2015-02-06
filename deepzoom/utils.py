"""django-deepzoom utils"""

from django import get_version



def is_django_version_greater_than(major=1, minor=4):
    """
    Returns whether Django version is greater than given major and minor numbers.
    Major and minor should be passed as ints.
    """
    _major, _minor = get_version().split('.')[:2]
    return (int(_major) >= major and int(_minor) > minor)


def get_subclasses(classes, iterator=0):
    """
    Returns a class and all its subclasses.
    """
    if not isinstance(classes, list):
        classes = [classes]
    
    if iterator < len(classes):
        classes += classes[iterator].__subclasses__()
        return get_subclasses(classes, iterator + 1)
    else:
        return classes


def receiver_subclasses(signal, sender, _dispatch_uid, **kwargs):
    """
    Replaces single-class `receiver` decorator with one that can register 
    signals for a class and all of its subclasses.
    """
    def _decorator(func):
        _senders = get_subclasses(sender)
        for _sender in _senders:
            signal.connect(func,
                           sender=_sender,
                           dispatch_uid=_dispatch_uid + '_' + _sender.__name__,
                           **kwargs)
        return func
    return _decorator


#EOF - django-deepzoom utils