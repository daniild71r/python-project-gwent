# python-project-gwent

>>> Список изменений (v1.1)

1 - Отрисовка отдельных игровых элементов инкапсулирована в отдельные классы во избежание дублирования кода, другие незначительные улучшения в архитектуре

2 - Командиры теперь действуют не только на юнитов, разыгранных до них, а на всех юнитов в ряду

3 - Игровой процесс стал более стратегически содержательным: теперь у игроков есть колода из 20 карт, и только 10 юнитов из 20 находятся в стартовой руке, каждая партия ведется до победы в двух раундах, в начале каждого раунда игрок получает одну дополнительных карту из колоды

4 - Поведение бота стало относительно осмысленным, он не разбрасывается картами попусту и не пропускает ходы, когда это ему невыгодно

5 - Для увеличения сложности бот получает небольшое преимущество в силе юнитов

6 - Новый класс карт - шпион, при разыгрывании шпиона игрок берет 2 юнита из колоды. Шпион и командир теперь отличимы от обычных юнитов на игровом поле.

>>> Список изменений (v1.2)

1 - В начале игры игроку предлагается выбрать уровень сложности. Этот уровень будет определять среднюю силу юнитов противника.

2 - В игру добавлены фракции! На данный момент их две: Королевства Севера и Нильфгаард. Принадлежность колоды к фракции определяет процентное соотношение карт особых типов в ней, а значит, и стратегию. У Королевств Севера преобладают командиры, у Нильфгаарда же - шпионы, причем нильфгаардские шпионы имеют большую силу по сравнению с северными. Противник играет колодой Королевств Севера.

3 - Переработан процесс генерации колоды для поддержания баланса: теперь <<неуникальная>> часть колоды, состоящая из обычных юнитов, генерируется один раз - и для игрока, и для бота. Колоды игрока и противника будут преобразовываться после принятия игроком решения о сложности и фракции.

4 - Различные улучшения в коде: весь текст перенесен в отдельный текстовый файл (например, для возможности легко локализовать игру на другой язык), часть глобальных игровых констант вынесена в классы, за пределами которых они не применяются, передача текстовой информации от игровых объектов интерфейсным унифицирована, а также другие незначительные изменения.

>>> Краткие правила

Данный проект является несколько упрощенным симулятором настольной игры <<Гвинт>>. Каждый раунд раунд игрок и противник-компьютер получают по 10 карт-юнитов, которых они выставляют на поле боя в один из трех рядов: рукопашный, стрелковый или осадный (для каждого юнита его тип заранее фиксирован), с целью получить наибольшую суммарную боевую мощь на поле. Уникальные классы юнитов: коммандир, увеличивающий силу всех других юнитов в своем ряду на один, и шпион, позволяющий игроку получить 2 дополнительных юнита. Каждый из игроков может в некоторый момент сдать ход, не разыгрывая карты, что будет означать, что следующий ход второго игрока будет последним, и затем будут подведены итоги раунда. В раунде побеждает игрок с большей суммой очков на своей половине поля, партия ведется до победы в двух раундах.