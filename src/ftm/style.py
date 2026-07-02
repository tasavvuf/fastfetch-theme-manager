class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    HEADER = "\033[44;37m"

    @staticmethod
    def print_header(text: str):
        print(f"\n{Style.HEADER}  {text.center(60)}  {Style.RESET}\n")

    @staticmethod
    def success(text: str):
        print(f"{Style.GREEN}* {text}{Style.RESET}")

    @staticmethod
    def error(text: str):
        print(f"{Style.RED}* {text}{Style.RESET}")

    @staticmethod
    def info(text: str):
        print(f"{Style.BLUE}* {text}{Style.RESET}")

    @staticmethod
    def warning(text: str):
        print(f"{Style.YELLOW}* {text}{Style.RESET}")
