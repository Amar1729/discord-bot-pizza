import mock
import pytest

import bot


@pytest.fixture()
def user_dict():
    return [
        {
            "name": "name1",
            "current": False,
        },
        {
            "name": "name2",
            "current": True,
        },
        {
            "name": "name3",
            "current": False,
        },
    ]


@mock.patch("bot.Pizza._read")
def test_pizza_users(pizza_read, user_dict) -> None:
    pizza_read.return_value = user_dict
    assert bot.Pizza.users() == ["name1", "name2", "name3"]


@mock.patch("bot.Pizza._write")
@mock.patch("bot.Pizza._read")
def test_pizza_set_user(pizza_read, pizza_write, user_dict) -> None:
    pizza_read.return_value = user_dict
    bot.Pizza.set_user("name1")

    user_dict[0]["current"] = True
    user_dict[1]["current"] = False

    pizza_write.assert_called_once_with(user_dict)


@mock.patch("bot.Pizza._write")
@mock.patch("bot.Pizza._read")
def test_pizza_set_user_invalid(pizza_read, pizza_write, user_dict) -> None:
    pizza_read.return_value = user_dict
    bot.Pizza.set_user("name_non_existent")
    pizza_write.assert_not_called()


@pytest.mark.parametrize(("jumps", "next_idx"), [
    (0, 1),
    (1, 2),
    (2, 0),
    (-1, 0),
])
@mock.patch("bot.Pizza._write")
@mock.patch("bot.Pizza._read")
def test_pizza_next_p(pizza_read, pizza_write, user_dict, jumps: int, next_idx: int) -> None:
    pizza_read.return_value = user_dict
    bot.Pizza.next(jumps)

    user_dict[1]["current"] = False
    user_dict[next_idx]["current"] = True

    pizza_write.assert_called_once_with(user_dict)
