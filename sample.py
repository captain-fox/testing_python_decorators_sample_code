import pytest


class User:
    """
    A substitute for actual user.
    We only need to test whether `user.is_manager` evaluates to True or False
    """

    def __init__(self, is_manager: bool):
        self.is_manager = is_manager


def using_email_address(function):
    def wrapper(user, **kwargs):
        from_email = 'management@ecorp.com' if user.is_manager else 'internal@ecorp.com'
        return function(user=user, from_email=from_email, **kwargs)

    return wrapper


# @using_email_address
# def notify_by_email(user, from_email, **kwargs):
#     """
#     This method obviously won't run, it's here to demonstrate what is the potential use of
#     `using_email_address` decorator
#     :param user:
#     :param from_email:
#     :param kwargs:
#     :return:
#     """
#     send_mail(
#         subject='Service email alert',
#         message='If you don\'t see content of this email please enable html.',
#         from_email=f'E-Corp <{from_email}>',
#         recipient_list=[user.email, ],
#         html_message=render_to_string(...),
#     )


@pytest.fixture
def manager():
    return User(is_manager=True)


@pytest.fixture
def regular():
    return User(is_manager=False)


def test_should_select_outgoing_address_for_managers(manager: User):
    @using_email_address
    def to_be_decorated(user, from_email, **kwargs):
        assert user is manager
        assert from_email == 'management@ecorp.com'

    to_be_decorated(manager)


def test_should_select_outgoing_address_for_regular_users(regular: User):
    @using_email_address
    def to_be_decorated(user, from_email, **kwargs):
        assert user is regular
        assert from_email == 'internal@ecorp.com'

    to_be_decorated(regular)


def test_should_fail_to_select_regular_outgoing_address_for_managers(manager: User):
    @using_email_address
    def to_be_decorated(user, from_email, **kwargs):
        assert user is manager
        with pytest.raises(AssertionError):
            assert from_email == 'internal@ecorp.com'

    to_be_decorated(manager)


def test_should_fail_to_select_manager_outgoing_address_for_regular_users(regular: User):
    @using_email_address
    def to_be_decorated(user, from_email, **kwargs):
        assert user is regular
        with pytest.raises(AssertionError):
            assert from_email == 'management@ecorp.com'

    to_be_decorated(regular)


# ----------- If decorated function takes arbitrary number of keyword arguments or
# ----------- you don't want to hassle with listing all required arguments:

def test_should_select_outgoing_address_for_managers_with_kwargs(manager: User):
    @using_email_address
    def to_be_decorated(**kwargs):
        assert kwargs.pop('from_email') == 'management@ecorp.com'
        assert kwargs.pop('user') == manager

    to_be_decorated(user=manager)


def test_should_select_outgoing_address_for_customers_with_kwargs(regular: User):
    @using_email_address
    def to_be_decorated(**kwargs):
        assert kwargs.pop('from_email') == 'internal@ecorp.com'
        assert kwargs.pop('user') == regular

    to_be_decorated(user=regular)
