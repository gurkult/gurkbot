from .bot import Bot


def main() -> None:
    """Starts bot."""
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
