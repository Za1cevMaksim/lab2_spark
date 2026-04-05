# Лабораторная работа 2

## Описание
Исследование производительности Apache Spark на кластере Hadoop с различным количеством DataNode (1 и 3). 
Сравнение базовой и оптимизированной версий Spark-приложения с использованием кэширования, репартиционирования и настройки shuffle.

### Датасет

https://www.kaggle.com/datasets/viridianachow/online-retail-uci-dataset

**Online Retail** 
- **Строк:** ~542k
- **Столбцов:** 8 (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)
- **Типы данных:** int, double, string, date

## Запуск
# Дайте права на выполнение
chmod +x run.sh
# Запустите скрипт
./run.sh
