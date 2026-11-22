def can_be_awakened(group: str, suit_or_set: str, value: str) -> bool:
    if suit_or_set.casefold() in ["death", "time"] or group.casefold() == "face":
        return False

    return is_card_value(value)


def is_card_value(unknown: str) -> bool:
    try:
        int(unknown)
        return True
    except ValueError:
        if unknown.casefold() == "ace":
            return True
        else:
            return False


def get_readable_name(group: str, suit_or_set: str, value: str) -> str:
    if group.casefold() == "face":
        result = value
    else:
        result = ""

        if can_be_awakened(group, suit_or_set, value):
            result += f"{group.title()} "

        result += value

        if is_card_value(value):
            result += f" of {suit_or_set.title()}"

    return result


def get_wiki_name(group: str, suit_or_set: str, value: str) -> str:
    group = group.title()
    suit_or_set = suit_or_set.title()

    if value.endswith(" (Difficulty)"):
        value = value[: -len(" (Difficulty)")]

    if value == "???":
        value = "Anglerfish"

    if group.casefold() == "face":
        result = f"Card {suit_or_set} {value}.png"
    else:
        result = f"Card {suit_or_set} {value} {group}.png"

    return result
