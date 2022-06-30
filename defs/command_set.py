from db.sql_aclhemy import db
from defs.gen_button import genButton as gb


def command_list(id_tg_chat: int):
    l_commands, l_states = db.command_list(id_tg_chat)
    dict_state = {True: '✅', False: '❌'}
    l_text = []
    l_callback = []
    for command, state in zip(l_commands, l_states):
        l_text.append(f'{command}: {dict_state.get(state)}')
        l_callback.append(f'comm_{int(state)}_{command}')

    inline_b = gb.inline_b(l_text, l_callback)
