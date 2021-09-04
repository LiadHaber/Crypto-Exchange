import sqlalchemy as db
import requests
from sqlalchemy.engine.base import Connection
from datetime import datetime

def databse_connection() -> Connection:
    """
    Create Connection To mysql DataBase

    Returns:
        Connection: DB Connection Objcet
    """
    config = {
        'host': 'db',
        'port': 3306,
        'user': 'root',
        'password': open(r'/run/secrets/db_password', 'r').read(),
        'database': 'crypto'
    }
    
    db_user = config.get('user')
    db_pwd = config.get('password')
    db_host = config.get('host')
    db_port = config.get('port')
    db_name = config.get('database')
    
    connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
    engine = db.create_engine(connection_str)
    connection =  engine.connect()
    return connection


def get_bitcoin_rate() -> float:
    """
    Get Current Bitcoin -> USD Rate From CoinAPI

    Returns:
        rate: The Current BitCoin -> USD Rate
    """
    try:
        res = requests.get('https://rest.coinapi.io/v1/exchangerate/BTC/USD', headers={'X-CoinAPI-Key' : api_key}).json()
        rate = res['rate']
        return rate
    except Exception as e:
        print(e)
        get_bitcoin_rate()

def get_raw_data() -> dict:
    """
    Retrive Raw Data From DB

    Returns:
        dict: Dict Object Representing The Data From The DB  
    """
    db_data = connection.execute('select max(iteration_id),sum(current_rate),max(current_rate), min(current_rate) from bitcoin_rates').fetchone()
    if db_data[0] is not  None:
        return {'num_iterations':db_data[0], 'current_sum' : db_data[1],'max_rate' :db_data[2], 'min_rate' : db_data[3]}
    else:
        # For The First Script Run Time
        return {'num_iterations': 0, 'current_sum': 0, 'max_rate': 0, 'min_rate': 0}

def calculate_new_avarage(divider:int, rates_sum:float) -> float:
    """
        Compute The New Avarage Rate Of Bitcoin
    Args:
        divider (int): The Divider
        rates_sum (float): Sum Of Bitcoin Rates From First To Current Script Run

    Returns:
        float: The New Avarage
    """
    return rates_sum / divider

def _insert_into_db(current_rate: float, avarage_rate: float) -> None:
    """
    Insert New Values Into The DB

    Args:
        current_rate (float): Current Bitcoin Rate
        avarage_rate (float): Bitcoin Rates Avarage From First To Current Script Run
    """
    connection.execute(f'insert into bitcoin_rates (current_rate,avarage_rate) values({current_rate}, {avarage_rate})')

def _print(max_rate:float, min_rate:float, avarage_rate:float, recommendation:bool, time_stamp: str, current_rate: float) -> None:
    print('Time Stamp:', time_stamp)
    print('Current Rate:', current_rate)
    print('Max Rate:',max_rate)
    print('Min Rate:',min_rate)
    print('Avg Rate:', avarage_rate)
    print('Should You Buy?', recommendation,'\n\n')

def get_last_5_rows_avg() -> float:
    """
    Retrive Last 5 DB Rows Rolling Avarage
    
    Returns:
        float: Last 5 DB Rows Rolling Avarage
    """
    query = connection.execute('select avg(current_rate) from ( select * from bitcoin_rates order by iteration_id desc limit 5) last5_rows_query order by iteration_id;').fetchone()[0]
    if query is not None:
        return query
    return 0

def should_buy(current_rate:float, last5_min_avg:float) -> bool:
    """
    Decide Wether Or Not The User Should Buy Bitcoin Now. Based On Comparison Between The Current Rate And Last 5 DB Rows Rolling Avarage

    Args:
        current_rate (float): The Current BitCoin Rate
        last5_min_avg (float): Last 5 DB Rows Rolling Avarage
    
    Returns:
        bool: Should The User Buy Bitcoin
    """
    return current_rate < last5_min_avg

def _close_db_connection() -> None:
    connection.close()
    



if __name__ == '__main__':
    connection = databse_connection()
    api_key = open(r'/run/secrets/api_key', 'r').read()
    current_bit_rate = get_bitcoin_rate()
    current_db_data = get_raw_data()
    new_avarage = calculate_new_avarage(current_db_data['num_iterations'] + 1, current_db_data['current_sum'] + current_bit_rate)
    max_rate = current_bit_rate if current_bit_rate > current_db_data['max_rate'] else current_db_data['max_rate']
    min_rate = current_bit_rate if current_bit_rate < current_db_data['min_rate'] else current_db_data['min_rate']
    last_5_rows_avg = get_last_5_rows_avg()
    _insert_into_db(current_bit_rate, new_avarage)
    recommendation = should_buy(current_bit_rate, last_5_rows_avg)
    _print(max_rate, min_rate, new_avarage, recommendation, datetime.now().strftime('%d-%m-%Y %H:%M:%S'), current_bit_rate)
    _close_db_connection()
