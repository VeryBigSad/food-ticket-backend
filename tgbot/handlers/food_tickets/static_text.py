get_qr_code_success = 'ебать, лови код id={id}, type={type}, date_usable_at={date_usable_at}, owner={owner},' \
                      ' sponsor={sponsor}, code={encoded}'
share_qr_code_success = 'скинул код твоему другу {telegram_account}'
share_qr_code_usage = 'Напиши /share_code @telegram_username чтобы отдать свой билет на еду сегодня!'
unknown_account_to_share_to = 'Не знаю того, кому ты пытаешься отдать обед ({username}).\n' \
                              'Может, ты ошибся в написании? Или твой друг еще не писал мне?'
# TODO: поменять формулировку
no_food_right = 'Сорян, кажется, у тебя нет прав на питание.'
no_food_right_and_no_ticket = 'Сорян, кажется, у тебя нет ни возможности создать талончик, ни нет свободного.'
you_already_used_food_ticket = 'Кажется, ты уже сделал тикет (id={id}) и использовал его.\n' \
                               'Ты не можешь их генерить бесконечно, только один!'
you_gave_food_ticket_away = 'Кажется, ты уже сделал тикет и отдал его человеку по имени {owner}.\n' \
                            'Ты не можешь их генерить бесконечно, только один!'

# TODO: поменять формулировку
share_to_student_can_create_a_ticket = 'Сорян, {first_name} не может получить талончик т.к.' \
                                       ' он еще не использовал свое сегодняшнее право на еду'
share_to_student_already_has_a_ticket = 'Сорян, {first_name} не может получить талончик т.к.' \
                                        ' он у него уже есть (на сегодня, {ft_type})'
account_share_to_not_registered = 'Я видел {username}, но он еще не зарегистрирован.\n' \
                                  'Попроси его сделать /register, и тогда я смогу дать ему талончик!'

you_sure_you_want_to_create_ticket_and_share_it = 'Ты уверен что ты хочешь создать тикет на ' \
                                                  'сегодня на {ft_type} чтобы его получил {first_name} '
you_sure_you_want_to_giveaway_your_ticket = 'Ты уверен чтобы {first_name} стал владельцем ' \
                                            'твоего талончика на {usable_at_date}, на {ft_type}'

someone_shared_ticket_with_you = '{first_name} подарил тебе талончик на {type} {date_usable_at}!\n' \
                                 'Напиши /get_code чтобы им воспользоваться (или /share_code ' \
                                 'чтобы отдать кому-то еще)!'

# keyboard static text
confirm_ticket_share = 'Да, отдать талончик ✅'
decline_ticket_share = 'Отмена ❌'
