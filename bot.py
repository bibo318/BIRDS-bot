import base64
import json
import os
import random
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime
from birdx import Birdx
from colorama import Fore, Style, init

# Khởi tạo colorama
init(autoreset=True)

def print_(word, color=Fore.WHITE):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"{color}[{now}] {word}{Style.RESET_ALL}")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_query():
    try:
        with open('birdx_query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        print_(f"Đã tải {len(queries)} truy vấn từ birdx_query.txt.", color=Fore.CYAN)
        return queries
    except FileNotFoundError:
        print_("Không tìm thấy file birdx_query.txt.", color=Fore.RED)
        return []
    except Exception as e:
        print_(f"Lấy truy vấn không thành công: {str(e)}", color=Fore.RED)
        return []

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def remaining_time(times):
    hours, remainder = divmod(times, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"Thời gian còn lại để nâng cấp: {int(hours)} Giờ {int(minutes)} Phút {int(seconds)} Giây"

def main():
    selector_task = input("Tự động xóa nhiệm vụ y/n: ").strip().lower()
    selector_games = input("Tự động chơi game y/n: ").strip().lower()
    clear_terminal()
    while True:
        birdx = Birdx()
        queries = load_query()
        sum = len(queries)
        delay = int(1 * random.randint(3600, 3650))
        start_time = time.time()
        for index, query in enumerate(queries, start=1):
            print_(f"========== Tài khoản {index}/{sum} ===========", color=Fore.YELLOW)
            print_('Đang lấy thông tin người dùng...', color=Fore.CYAN)
            data_user_info = birdx.get_user_info(query)
            if data_user_info is not None:
                username = data_user_info.get('telegramUserName', 'Không xác định')
                telegram_id = data_user_info.get('telegramId', 'Không xác định')
                telegram_age = data_user_info.get('telegramAge', 'Không xác định')
                total_rewards = data_user_info.get('balance', 0)
                incubationSpent = data_user_info.get('incubationSpent', 0)
                print_(f"TGID: {telegram_id} | Tên: {username} | Tuổi: {telegram_age} | Phần thưởng: {total_rewards}", color=Fore.GREEN)

                if incubationSpent == 0:
                    birdx.upgraded(query)
                
                data_info = birdx.get_info(query)
                if data_info is not None:
                    level = data_info.get('level', 0)
                    status = data_info.get('status', 0)
                    print_(f"Cấp độ: {level} | Chim: {data_info.get('birds')}", color=Fore.CYAN)
                    upgradedAt = data_info.get('upgradedAt', 0) / 1000
                    duration = data_info.get('duration', 0)
                    now = time.time()
                    upgrade_time = 3600 * duration
                    if now >= (upgradedAt + upgrade_time):
                        if status == "confirmed":
                            print_('Đang nâng cấp...', color=Fore.YELLOW)
                            birdx.upgraded(query)
                        else:
                            data_confirmed = birdx.confirm_upgrade(query)
                            if data_confirmed is not None:
                                print_("Nâng cấp đã được xác nhận...", color=Fore.GREEN)
                                birdx.upgraded(query)
                    else:
                        print_(remaining_time((upgradedAt + upgrade_time) - now), color=Fore.MAGENTA)
                
                if selector_task == "y":
                    print_("Bắt đầu xóa nhiệm vụ", color=Fore.YELLOW)
                    birdx.clear_task(query)
                
                if selector_games == "y":
                    print_("Bắt đầu chơi game", color=Fore.YELLOW)
                    birdx.join_game(query)

            else:
                print_('Không tìm thấy người dùng', color=Fore.RED)

        end_time = time.time()
        total = delay - (end_time - start_time)
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        if total > 0:
            print_(f"[ Khởi động lại sau {int(hours)} Giờ {int(minutes)} Phút {int(seconds)} Giây ]", color=Fore.CYAN)
            time.sleep(total)

if __name__ == "__main__":
    main()
