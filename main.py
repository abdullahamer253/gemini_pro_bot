
from gemini_pro_bot.bot import start_bot
from gemini_pro_bot2.bot import start_bot1

from multiprocessing import Pool

def run_bot(func):
  func()  # Call the provided function

if __name__ == "__main__":
  num_processes = 2  # Adjust this value as needed (start with a lower number)
  with Pool(processes=num_processes) as pool:
    pool.map(run_bot, [start_bot, start_bot1])  # Run functions concurrently

