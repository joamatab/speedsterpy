from loguru import logger
import os

def main():
    print("Speedster, Version 1.2")
    logger.info("Project File: {}".format(os.path.abspath(__file__)))
    
if __name__ == "__main__":
    main()