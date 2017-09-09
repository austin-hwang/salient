import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import sys
import json
# import quandl
# import quandl.errors.quandl_error
import pandas
import re
import random
from operator import itemgetter
import statistics
import yahoo_finance as yf

# quandl.ApiConfig.api_key = "dpWaM-T_pzLD58Hy_wjH"

SAMPLE_SIZE = 50


def camelcase(string):
    s = [c for c in string.title() if not c.isspace()]
    s[0] = s[0].lower()
    return ''.join(s)


def digest(symbol):
    # Return summary of interesting features of a stock

    sector = get_sector(symbol)

    if sector is None:
        return {'error': 'no data'}

    related = get_stocks_in_sector(sector)
    related = random.sample(related, SAMPLE_SIZE) + [symbol]

    data = compile_data(related)

    if len(data) == 0 or symbol not in data:
        return {'error': 'no data'}

    # print('\n\n')
    #
    # for field in fields:
    #     print(field, ">>>", "PERCENTILE:", compute_percentile(symbol, field, data), "STDEVS:",
    #           compute_stdev_from_mean(symbol, field, data), "STDEV:", compute_std(field, data), "MEAN:",
    #           compute_mean(field, data))
    #
    # print('\n\n')

    return {
        'sample_size': SAMPLE_SIZE,
        'features': {field: {
            'value': data[symbol][field],
            'percentile': compute_percentile(symbol, field, data),
            'stddevs_from_mean': compute_stdev_from_mean(symbol, field, data),
            'stddev': compute_std(field, data),
            'mean': compute_std(field, data),
        } for field in fields},
        'salient_fields': [field for field in fields if
                           compute_stdev_from_mean(symbol, field, data) is not None and
                           compute_stdev_from_mean(symbol, field, data) != "infinity" and
                           compute_stdev_from_mean(symbol, field, data) > 2.0],
        'neg_salient_fields': [field for field in fields if
                           compute_stdev_from_mean(symbol, field, data) is not None and
                           compute_stdev_from_mean(symbol, field, data) != "infinity" and
                           compute_stdev_from_mean(symbol, field, data) < -2.0],
        'related': random.sample(related, 10)
    }


# def download_data(symbols, rows=1):
#     data = {}
#     for i, s in enumerate(symbols):
#         try:
#             print("[ {}% ] Downloading {}...".format(i / len(symbols) * 100, s))
#             data[s] = quandl.get("WIKI/" + s, rows=rows)
#         except quandl.errors.quandl_error.NotFoundError:
#             print("--> invalid ticker.")
#
#     return data

fields = ['price', 'ppe', 'volume', 'market_cap', 'div_yield', 'percent_change', 'avg_daily_volume', 'peg']


def compile_data(symbols):
    data = {}

    for i, s in enumerate(symbols):
        # print("[ {}% ] Downloading {}...".format(i / len(symbols) * 100, s))
        try:
            d = yf.Share(s)
            data[s] = {
                'price': d.get_price(),
                'ppe': d.get_price_earnings_ratio(),
                'market_cap': d.get_market_cap(),
                'div_yield': d.get_dividend_yield(),
                'volume': d.get_volume(),
                'percent_change': d.get_percent_change(),
                'avg_daily_volume': d.get_avg_daily_volume(),
                'peg': d.get_price_earnings_growth_ratio(),
            }

            for field in fields:
                a = data[s][field]
                if a is not None:
                    if a[-1] == 'B':
                        a = float(a[:-1]) * 10 ** 9
                    elif a[-1] == 'M':
                        a = float(a[:-1]) * 10 ** 6
                    elif a[-1] == 'K':
                        a = float(a[:-1]) * 10 ** 3
                    elif a[-1] == '%':
                        a = float(a[:-1])
                    else:
                        a = float(a)

                    data[s][field] = a
        except Exception as e:
            pass
            # print("error:", e)

    return data


def compute_percentile(symbol, field, data):
    values = sort_symbols(field, data)
    if symbol in values and len(values) > 1:
        i = values.index(symbol)
        return str(i / (len(values) - 1) * 100)
    else:
        return None


def compute_rank(symbol, field, data):
    values = sort_symbols(field, data)
    if symbol in values:
        return list(reversed(sort_symbols(field, data))).index(symbol) + 1
    else:
        return None


def sort_symbols(field, data):
    values = []

    for s in data:
        if data[s][field] != None:
            values.append((s, data[s][field]))

    # print(field, values)

    values = sorted(values, key=itemgetter(1))

    return [y[0] for y in values]


def slice_symbols_above_percentile(percentile, field, data):
    return [s for s in data if compute_percentile(s, field, data) > percentile]


def compute_mean(field, data):
    return statistics.mean([data[s][field] for s in data if data[s][field] is not None])


def compute_std(field, data):
    # print([data[s][field] for s in data])
    return statistics.stdev([data[s][field] for s in data if data[s][field] is not None])


def compute_stdev_from_mean(symbol, field, data):
    # print(symbol, field)
    value = data[symbol][field]
    if value is not None:
        if compute_std(field, data) != 0:
            return (value - compute_mean(field, data)) / compute_std(field, data)
        else:
            return "infinity"
    else:
        return None


def get_related(symbol):
    # Return list of related stocks

    return get_stocks_in_sector(get_sector(symbol))


def get_sector(symbol):
    # Get the sector name of a stock

    map = pandas.read_csv("sector_map.csv")
    sector = map.query("SYMBOL == '{}'".format(symbol))["SECTOR"]
    if len(sector.values) > 0:
        return sector.values[0]
    else:
        return None


def get_stocks_in_sector(sector):
    # Get a list of stocks in a sector by sector name
    symbols = pandas.read_csv("sectors/{}.csv".format(camelcase(sector)), header=None, usecols=[0]).values.tolist()
    symbols = [re.sub('\s+', '', entry[0]) for entry in symbols]
    symbols = [s for s in symbols if len(s) > 0]

    return symbols


if __name__ == '__main__':
    # USAGE: digest.py SYMBOL

    symbol = sys.argv[1]

    # print(symbol)
    # print("SECTOR:", get_sector(symbol))
    # print("RELATED:", get_related(symbol))

    # print("DIGEST =========================")
    try:
        print(json.dumps(digest(symbol)))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
