import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRAIN = ROOT / "brain"
for path in (str(ROOT), str(BRAIN)):
    if path not in sys.path:
        sys.path.insert(0, path)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import core
from connection import TelegramConnection


def main() -> None:
    core.setup_console_logging()

    bot = TelegramConnection()
    bot.connect(core.run)
    bot.start()


if __name__ == "__main__":
    main()


# prosesnya kurang lebih koneksi ke on message yang mana disini callabel adalah fungsi yang mengmbalikan string dan menerima string