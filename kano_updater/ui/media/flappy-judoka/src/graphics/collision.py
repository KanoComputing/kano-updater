
# Code from http://www.pygame.org/wiki/FastPixelPerfect, 29 September 2015


def check_collision(obj1, obj2):
    """checks if two objects have collided, using hitmasks"""
    try:
        rect1, rect2, hm1, hm2 = obj1.rect, obj2.rect, obj1.hitmask, obj2.hitmask
    except AttributeError:
        return False
    rect = rect1.clip(rect2)
    if rect.width == 0 or rect.height == 0:
        return False
    x1, y1, x2, y2 = rect.x - rect1.x, rect.y - rect1.y, rect.x - rect2.x, rect.y - rect2.y
    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hm1[x1 + x][y1 + y] and hm2[x2 + x][y2 + y]:
                return True
            else:
                continue
    return False


def get_colorkey_hitmask(image, rect, key=None):
    """returns a hitmask using an image's colorkey.
       image->pygame Surface,
       rect->pygame Rect that fits image,
       key->an over-ride color, if not None will be used instead of the image's colorkey"""
    if key is None:
        colorkey = image.get_colorkey()
    else:
        colorkey = key
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not image.get_at((x, y)) == colorkey)
    return mask


def get_alpha_hitmask(image, rect, alpha=0):
    """returns a hitmask using an image's alpha.
       image->pygame Surface,
       rect->pygame Rect that fits image,
       alpha->the alpha amount that is invisible in collisions"""
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not image.get_at((x, y))[3] == alpha)
    return mask


def get_colorkey_and_alpha_hitmask(image, rect, key=None, alpha=0):
    """returns a hitmask using an image's colorkey and alpha."""
    if key is None:
        colorkey = image.get_colorkey()
    else:
        colorkey = key
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not (image.get_at((x, y))[3] == alpha or
                                image.get_at((x, y)) == colorkey))
    return mask


def get_full_hitmask(image, rect):
    """returns a completely full hitmask that fits the image,
       without referencing the images colorkey or alpha."""
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(True)
    return mask
