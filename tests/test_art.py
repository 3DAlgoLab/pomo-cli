"""Tests for the pomodoro banner grouping."""

from pomo.art import TOMATO, format_banner, print_banner


def test_no_extra_space_below_group_size():
    assert format_banner(3) == TOMATO * 3


def test_one_space_every_four():
    assert format_banner(4) == TOMATO * 4
    assert format_banner(5) == TOMATO * 4 + " " + TOMATO
    assert format_banner(9) == TOMATO * 4 + " " + TOMATO * 4 + " " + TOMATO


def test_nonpositive_is_empty():
    assert format_banner(0) == ""
    assert format_banner(-1) == ""


def test_print_banner_keeps_trailing_space(capsys):
    print_banner(5)
    assert capsys.readouterr().out == format_banner(5) + " "
