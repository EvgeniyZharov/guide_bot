from aiogram.dispatcher.filters.state import StatesGroup, State

MAIN_TOKEN = ""


host = ""
user = ""
password = ""

db_version = "1.0"

BASE_IMAGE_ID = ""


# ["Начать викторину", "Посмотреть статистику", "Виртуальный гид", "Узнать про HSE Travel"]
class FSMWorkProgram(StatesGroup):
    # Status for Main menu
    main_menu = State()

    # Quiz menu
    user_quiz_menu = State()
    # 1-st path
    get_statistic = State()
    # 2-nd path
    get_quiz_theme = State()
    get_quiz = State()
    run_quiz = State()

    # Guide menu
    get_towns = State()
    get_routes = State()
    choice_route = State()
    # 1-st path
    start_route = State()

    # About us menu
    about_us_menu = State()

    ####################
    #    For admins    #
    ####################

    # Admin main menu
    to_admin_main_menu = State()
    admin_main_menu = State()
    admin_settings = State()

    # Virtual Guide Settings

    # Landmark settings
    landmark_settings = State()
    # Set new town
    set_new_town = State()
    save_new_town = State()
    # Set new landmark
    set_new_landmark = State()
    set_town_id_landmark = State()
    set_title_landmark = State()
    set_image_link_landmark = State()
    save_new_landmark = State()
    # Set new facts about landmark
    set_new_fact = State()
    set_town_id_fact = State()
    set_landmark_id_fact = State()
    set_title_fact = State()
    set_text_fact = State()
    set_audio_fact = State()
    set_image_link_fact = State()

    # Quiz settings

    # Quiz settings
    quiz_settings = State()
    # Set new quiz group
    set_new_quiz_theme = State()
    set_quiz_theme_title = State()
    set_quiz_theme_description = State()
    # Set new quiz theme
    set_new_quiz = State()
    set_quiz_group_id = State()
    set_quiz_title = State()
    set_quiz_description = State()
    # Set new ask for quiz
    set_new_quiz_ask = State()
    set_quiz_theme_id_ask = State()
    set_quiz_id_ask = State()
    set_quiz_ask = State()
    set_questions = State()
    set_quiz_ask_image = State()

    #
    # Events part
    #

    # Events menu
    event_main_menu = State()
    choice_event = State()
    reg_on_event = State()

    # Trip menu
    trip_main_manu = State()
    choice_trip = State()
    trip_run = State()
    close_trip = State()


