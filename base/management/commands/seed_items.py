from django.core.management.base import BaseCommand
from base.models import Item


ITEMS = [
    # Оружие
    {'name': 'Механический Меч', 'slot': 'weapon', 'icon': '⚔️', 'description': 'Выкован из клавиатуры разработчика'},
    {'name': 'Лук Дебаггера', 'slot': 'weapon', 'icon': '🏹', 'description': 'Стреляет логами с точностью снайпера'},
    {'name': 'Кинжал Рефакторинга', 'slot': 'weapon', 'icon': '🗡️', 'description': 'Чистит легаси-код мгновенно'},
    # Броня
    {'name': 'Щит Документации', 'slot': 'armor', 'icon': '🛡️', 'description': 'Защищает от непонимания требований'},
    {'name': 'Броня Code Review', 'slot': 'armor', 'icon': '🔰', 'description': 'Закалена в тысячах пулл-реквестов'},
    # Обувь
    {'name': 'Кеды Деплоя', 'slot': 'boots', 'icon': '👟', 'description': 'Ускоряют сборку проекта в 2 раза'},
    {'name': 'Сапоги Релиза', 'slot': 'boots', 'icon': '👢', 'description': 'Уверенно шагают на продакшен'},
    # Аксессуар
    {'name': 'Кольцо Stack Overflow', 'slot': 'accessory', 'icon': '💍', 'description': 'Содержит ответы на все вопросы'},
    {'name': 'Амулет Git', 'slot': 'accessory', 'icon': '🔮', 'description': 'Хранит всю историю коммитов'},

    # Оружие (новые)
    {'name': 'Посох Архитектора', 'slot': 'weapon', 'icon': '🪄', 'description': 'Проектирует системы одним взмахом'},
    {'name': 'Молот Хотфикса', 'slot': 'weapon', 'icon': '🔨', 'description': 'Бьёт по багам прямо в продакшене'},
    {'name': 'Коса Деадлайна', 'slot': 'weapon', 'icon': '🔱', 'description': 'Наводит ужас на прокрастинаторов'},
    {'name': 'Пистолет Деплоя', 'slot': 'weapon', 'icon': '🔫', 'description': 'Один выстрел — один релиз'},
    {'name': 'Топор Легаси', 'slot': 'weapon', 'icon': '🪓', 'description': 'Рубит легаси-код без сожаления'},

    # Броня (новые)
    {'name': 'Шлем Сеньора', 'slot': 'armor', 'icon': '⛑️', 'description': 'Защищает от глупых вопросов на ревью'},
    {'name': 'Мантия DevOps', 'slot': 'armor', 'icon': '🥷', 'description': 'Позволяет деплоить бесшумно и незаметно'},
    {'name': 'Накидка Тимлида', 'slot': 'armor', 'icon': '🦸', 'description': 'Внушает уважение на стендапах'},
    {'name': 'Жилет Аналитика', 'slot': 'armor', 'icon': '🦺', 'description': 'Содержит карманы для метрик и KPI'},
    {'name': 'Плащ Инкогнито', 'slot': 'armor', 'icon': '🧥', 'description': 'Скрывает незавершённые ветки от тимлида'},

    # Обувь (новые)
    {'name': 'Тапочки Удалёнки', 'slot': 'boots', 'icon': '🩴', 'description': 'Максимальный комфорт при работе из дома'},
    {'name': 'Кроссовки Скрама', 'slot': 'boots', 'icon': '👠', 'description': 'Быстро бегут от спринта к спринту'},
    {'name': 'Ботинки Стартапа', 'slot': 'boots', 'icon': '🥾', 'description': 'Выдерживают любые пивоты'},

    # Аксессуар (новые)
    {'name': 'Очки Code Review', 'slot': 'accessory', 'icon': '🕶️', 'description': 'Видят баги насквозь'},
    {'name': 'Перчатки Хакера', 'slot': 'accessory', 'icon': '🧤', 'description': 'Не оставляют следов в git blame'},
    {'name': 'Часы Дедлайна', 'slot': 'accessory', 'icon': '⌚', 'description': 'Всегда показывают что времени нет'},
    {'name': 'Зелье Кофе', 'slot': 'accessory', 'icon': '☕', 'description': '+50 к концентрации на ночном дежурстве'},
    {'name': 'Свиток Docker', 'slot': 'accessory', 'icon': '📜', 'description': 'Запускает всё в контейнере'},
    {'name': 'Кулон CI/CD', 'slot': 'accessory', 'icon': '🔗', 'description': 'Автоматически собирает и деплоит'},
    {'name': 'Посох PM', 'slot': 'weapon', 'icon': '🪃', 'description': 'Возвращает задачи обратно в бэклог'},
]


class Command(BaseCommand):
    help = 'Заполняет базу стартовыми предметами'

    def handle(self, *args, **options):
        created = 0
        for data in ITEMS:
            _, is_new = Item.objects.get_or_create(name=data['name'], defaults=data)
            if is_new:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Готово! Добавлено предметов: {created}'))
