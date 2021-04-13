from aiogram.dispatcher.filters.state import State, StatesGroup


# States
class Menu(StatesGroup):
    global_menu = State()
    organaiser_menu = State()
    profile_menu = State()
    peoples_menu = State()
    faq_menu = State()


class ProfileMenu(StatesGroup):
    status = State()
    log_out = State()


class StatusChange(StatesGroup):
    change_data = State()
    change_status = State()
    proof_change_orange = State()
    proof_change_red = State()
    proof_change_green = State()
    input_sum_red = State()
    input_days_red = State()
    final_input_red = State()
    input_sum_orange = State()
    final_input_orange = State()
    return_to_orange = State()


class DataStatusChange(StatesGroup):
    proof_change_orange = State()
    proof_change_red = State()
    input_sum_red = State()
    input_days_red = State()
    final_input_red = State()
    input_sum_orange = State()
    final_input_orange = State()
    return_to_orange = State()


class Invite(StatesGroup):
    list_invite = State()

    start_orange_invitation = State()
    start_orange_invitation_check = State()
    input_sum_for_orange = State()

    start_red_invitation = State()
    start_red_invitation_check = State()
    input_sum_for_red = State()


class AboutMe(StatesGroup):
    check_input = State()
    check_input_about = State()
    check_input_name = State()


class Requisites(StatesGroup):
    requisites_menu = State()
    add_requisites_name = State()
    add_requisites_check = State()
    add_requisites_finish = State()
    edit_requisites = State()
    edit_requisites_name = State()
    edit_requisites_check = State()
    edit_requisites_finish = State()


class IntentionFrom(StatesGroup):
    list_intention = State()
    intention_settings = State()
    cancel_intention = State()
    change_intention = State()

    obligation_settings = State()
    obligation_send_proof = State()


class IntentionTo(StatesGroup):
    list_intention = State()
    intention_settings = State()
    cancel_intention = State()
    change_intention = State()

    obligation_settings = State()
    obligation_forgive_proof = State()


class ProofObligation(StatesGroup):
    list_obligation = State()
    list_obligation_check = State()


class BadObligation(StatesGroup):
    list_obligation = State()
    list_obligation_check = State()


class Participants(StatesGroup):
    to_help = State()
    select_participant = State()

    view_other_user = State()
    select_other_participant = State()


class Admin(StatesGroup):
    main_menu = State()
    send_menu = State()
    check_send_menu = State()


