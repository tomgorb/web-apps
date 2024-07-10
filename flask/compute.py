#! /usr/bin/env python3
# coding: utf-8

import argparse
import pandas as pd

def max(s, *_):
    return s.max()

def mean(s, *_):
    return s.mean()

def median(s, *_):
    return s.median() 

def min(s, *_):
    return s.min()

def quantile(s, p):
    return s.quantile(q=int(p)/100)

def std(s, *_):
    return s.std()

def sum(s, *_):
    return s.sum(min_count=1)

functions = {
    "max": max,
    "mean": mean,
    "median": median,
    "min": min,
    "quantile": quantile,
    "std": std,
    "sum": sum
    }

def get_stats(stats, period, data):
    r = {}
    d = data[(data["datetime"]>=period[0])&(data["datetime"]<=period[1])]
    for stat in stats:
        s, _, v = stat.partition(",")
        r[s+v] = functions[s](d["orders"], v)
    r['#days'] = len(pd.unique(d['datetime']))
    return pd.DataFrame.from_dict([r])


def parse_arguments():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="which",
        help="""Data source"""
    )

    parser.add_argument(
        "-n1",
        "--name1",
        type=str,
        help="""Name of the first period""",
        default='period1'
    )

    parser.add_argument(
        "-p1",
        "--period1",
        nargs=2,
        type=str,
        help="""Period: start_date end_date.
        With start_date and end_date in the %Y-%m-%d""",
        required=True
    )

    parser.add_argument(
        "-n2",
        "--name2",
        type=str,
        help="""Name of the second period""",
    )

    parser.add_argument(
        "-p2",
        "--period2",
        nargs=2,
        type=str,
        help="""Period: start_date end_date.
        With start_date and end_date in the %Y-%m-%d"""
    )

    parser.add_argument(
        "-n3",
        "--name3",
        type=str,
        help="""Name of the third period""",
    )

    parser.add_argument(
        "-p3",
        "--period3",
        nargs=2,
        type=str,
        help="""Period: start_date end_date.
        With start_date and end_date in the %Y-%m-%d"""
    )

    parser.add_argument(
        "-d",
        "--datafile",
        help="""CSV file containing data""",
        required=True
    )

    parser.add_argument(
        "-o",
        "--output",
        help="""Name of the output file"""
    )
    
    # Subparser for source
    parser_a = subparsers.add_parser("SOURCE",
                                     help="""Data source is SOURCE""")
    parser_a.add_argument(
        "-k",
        "--stats",
        nargs='+',
        help="""Stats desired in the output""",
        required=True
    )

    return parser.parse_args()


if __name__ == "__main__":
    data = pd.DataFrame()
    try:
        args = parse_arguments()
    except Exception as e:
        print(e)
    else:

        data = pd.read_csv(args.datafile, sep="|", header=0)
        data["datetime"] = pd.to_datetime(data["day"], format='%Y-%m-%d')
        data.drop(["day"], axis=1, inplace=True)

        periods = {
            args.name1: args.period1,
            }
        if args.name2:
            periods[args.name2] = args.period2
            if args.name3:
                periods[args.name3] = args.period3


        dfs = []
        for (name, period) in periods.items():
            print(period)
            df = get_stats(args.stats, period, data)
            df["name"] = name
            df["period"] = "between %s and %s"%(period[0], period[1])
            dfs.append(df)
            
        output_filename = args.output
        pd.concat(dfs).to_csv(output_filename, index=False)
