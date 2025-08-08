from aiogram.fsm.state import State, StatesGroup

class HumanDesignStates(StatesGroup):
    SELECT_LANGUAGE = State()
    MAIN_CONVERSATION = State()
    CONFIRM_SAVE_CHAT = State()