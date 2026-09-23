import argparse
from loan_model import train_and_save


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    train_and_save(args.csv)
