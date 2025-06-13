import math
import numpy as np

def game_core(number: int = 1) -> int:
    """Сначала устанавливаем любое random число "predict", а потом уменьшаем или
    увеличиваем его в зависимости от того, больше оно или меньше нужного "number".
    При этом ряд всех возможных чисел представляем себе в виде отрезка от 1 до 100 (включительно). 
    Если загаданное число "number" больше, чем предположенное "predict",
    то устанавливаем "predict" как начало отрезка, и в качестве следующего 
    предположения берем середину отрезка от "predict" до 100.
    Если же "number" меньше, чем "predict", то используем обратную логику.
    Округление в большую/меньшую сторону используем, чтобы сократить количество необходимых попыток.
    Функция принимает загаданное число и возвращает число попыток.

    Args:
        number (int, optional): Загаданное число. Defaults to 1.

    Returns:
        int: Число попыток
    """
    count = 0
    predict = np.random.randint(1, 101)
    predict_max = 100
    predict_min = 1

    while number != predict:
        count += 1
        if number > predict:
            predict_min = predict
            predict = math.ceil((predict_max + predict)/2)
        elif number < predict:
            predict_max = predict
            predict = math.floor((predict_min + predict)/2)

    return count

def score_game(random_predict) -> int:
    """За какое количество попыток в среднем за 10000 подходов угадывает наш алгоритм

    Args:
        random_predict ([type]): функция угадывания

    Returns:
        int: среднее количество попыток
    """
    count_ls = []
    #np.random.seed(1)  # фиксируем сид для воспроизводимости
    random_array = np.random.randint(1, 101, size=(10000))  # загадали список чисел

    for number in random_array:
        count_ls.append(random_predict(number))

    score = int(np.mean(count_ls))
    print(f"Ваш алгоритм угадывает число в среднем за: {score} попытки")

#Run benchmarking to score effectiveness of all algorithms
print('Run benchmarking for game_core_v3: ', end='')
score_game(game_core)    