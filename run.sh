#!/bin/bash
set -e 
# sudo apt update && sudo apt install -y openjdk-17-jdk python3-venv > /dev/null 2>&1

# export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
# export PATH=$JAVA_HOME/bin:$PATH

# if [ ! -d "venv" ]; then
#     python3 -m venv venv
# fi
# source venv/bin/activate
# pip install pyspark psutil matplotlib > /dev/null 2>&1

# echo "Зависимости установлены."
# mkdir -p results


set_replication() {
    local repl=$1
    sed -i "s/HDFS_CONF_dfs_replication=[0-9]/HDFS_CONF_dfs_replication=${repl}/g" docker-compose.yml
    echo "Репликация HDFS установлена в: ${repl}"
}

check_datanodes() {
    local expected=$1
    echo "Проверка активных DataNode (ожидаем: ${expected})"
    sleep 10
    docker exec namenode hdfs dfsadmin -report | grep "Live datanodes"
}

mkdir -p results


echo "Этап 1/2: Кластер с 1 DataNode"
set_replication 1

docker compose down -v > /dev/null 2>&1 || true
docker compose up -d --scale datanode=1
echo "Ожидание инициализации HDFS (45 сек)"
sleep 45
check_datanodes 1

echo "Загрузка данных в HDFS"
docker cp Online_Retail.csv namenode:/tmp/
docker exec namenode hdfs dfs -mkdir -p /data
docker exec namenode hdfs dfs -put -f /tmp/Online_Retail.csv /data/

echo "Эксперимент 1/4: 1 DN, Base"
EXP_DN_COUNT=1 python spark_app.py > results/exp_1dn_base.json

echo "Эксперимент 2/4: 1 DN, Opt"
EXP_DN_COUNT=1 python spark_app.py --opt > results/exp_1dn_opt.json


echo "Этап 2/2: Кластер с 3 DataNode"
set_replication 3

docker compose down -v
docker compose up -d --scale datanode=3
echo "Ожидание инициализации 3 узлов (60 сек)"
sleep 60
check_datanodes 3

echo "Загрузка данных в HDFS"
docker cp Online_Retail.csv namenode:/tmp/
docker exec namenode hdfs dfs -mkdir -p /data
docker exec namenode hdfs dfs -put -f /tmp/Online_Retail.csv /data/

echo "Эксперимент 3/4: 3 DN, Base"
EXP_DN_COUNT=3 python spark_app.py > results/exp_3dn_base.json

echo "Эксперимент 4/4: 3 DN, Opt"
EXP_DN_COUNT=3 python spark_app.py --opt > results/exp_3dn_opt.json

python merge_results.py

