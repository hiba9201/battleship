# Игра "Пчелиный бой"

Версия 1.1

Автор: Пелевина Анастасия (pelevina.2000@mail.ru)

## Описание

Приложение является реализацией игры "Морской бой" против бота с шестиугольным полем

## Состав

Консольная версия: `cbattlebee.py`

Логика игры: `environment.py`

## Консольная версия

Запуск: `./cbattlebe.py`

### Управление

* `show user | bot` - показать поле игрока | бота
* `auto` - расставить корабли на поле игрока автоматически
* `new` - начать новую игру
* `help` - показать справку по управлению
* `fire number LETTER` - выстрелить в заданную клетку (формат координат - *число БУКВА*)
* `quit` - закрыть приложение

#### Постановка корабля на поле
 `place ship_len rotation number LETTER`:
 - *ship_len* - длина корабля
 - *rotation* - поворот корабля относительно верхнего правого угла. 
 
    __Значения:__
     
        h - горизонатльно
        vr - вертикально вправо
        vl - вертикально влево

- *number LETTER* - координаты клетки в формате *число БУКВА*