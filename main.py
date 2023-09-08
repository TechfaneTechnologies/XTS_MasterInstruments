# -*- coding: utf-8 -*-
"""
    :description: A Python Script To Fetch and Save Symphony Fintech XTS API's Instrument/Contract Masters as CSV Files.
    :license: MIT.
    :author: Dr June Moone
    :created: On Monday March 27, 2023 01:30:30 GMT+05:30
"""
__author__ = "Dr June Moone"
__webpage__ = "https://github.com/MooneDrJune"
__license__ = "MIT"


import os

import requests

from json import JSONDecodeError

HEADERS = {"Content-Type": "application/json"}
BASE_URL = "https://developers.symphonyfintech.in/apimarketdata/instruments"
MASTER = "/master"
INDEXLIST = "/indexlist"
IL_PARAMS_NSE = {"exchangeSegment": 1}
IL_PARAMS_BSE = {"exchangeSegment": 11}

CM_HDR = "ExchangeSegment|ExchangeInstrumentID|InstrumentType|Name|Description|Series|NameWithSeries|InstrumentID|PriceBandHigh|PriceBandLow| FreezeQty|TickSize|LotSize|Multiplier|displayName|ISIN|PriceNumerator|PriceDenominator|FullDescription\n"
FO_HDR = "ExchangeSegment|ExchangeInstrumentID|InstrumentType|Name|Description|Series|NameWithSeries|InstrumentID|PriceBandHigh|PriceBandLow|FreezeQty|TickSize|LotSize|Multiplier|UnderlyingInstrumentId|UnderlyingIndexName|ContractExpiration|StrikePrice|OptionType|displayName|PriceNumerator|PriceDenominator|FullDescription\n"

exchangeSegmentList = [
    "NSECM",
    "NSEFO",
    "NSECD",
    "NSECO",
    "BSECM",
    "BSEFO",
    "BSECD",
    "BSECO",
    "NCDEX",
    "MSECM",
    "MSEFO",
    "MSECD",
    "MCXFO",
]


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), "csv"), exist_ok=True)
    exchange_wise_MC = dict.fromkeys(exchangeSegmentList, "")
    exchange_wise_MC_Idx = dict.fromkeys(["NSECM", "BSECM"], "")
    with requests.session() as session:
        for exchange, params in (
            ("NSECM", IL_PARAMS_NSE),
            ("BSECM", IL_PARAMS_BSE),
        ):  # noqa E501
            try:
                response = session.get(
                    BASE_URL + INDEXLIST,
                    params=params,  # noqa E501
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as _exception:
                print(str(_exception))
            else:
                try:
                    data = response.json()
                except JSONDecodeError:
                    print(
                        f"Failed to Decode Response Json for params: {params}",  # noqa E501
                        f"Respose was: {response.content.decode('utf-8')}",
                        "Continuing Loop to fetch other exchange...",
                        sep="\n",
                        end="\n\n",
                    )
                    continue
                else:
                    exchange_wise_MC_Idx[exchange] = data
        for exchange in exchangeSegmentList:
            try:
                response = session.post(
                    BASE_URL + MASTER,
                    headers=HEADERS,
                    json=dict(exchangeSegmentList=[exchange]),  # noqa E501
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as _exception:
                print(str(_exception))
            else:
                try:
                    data = response.json()
                except JSONDecodeError:
                    print(
                        f"Failed to Decode Response Json for Exchange: {exchange}",  # noqa E501
                        f"Respose was: {response.content.decode('utf-8')}",
                        "Continuing Loop to fetch other exchange...",
                        sep="\n",
                        end="\n\n",
                    )
                    continue
                else:
                    exchange_wise_MC[exchange] = data

    for exchange, data in exchange_wise_MC.items():
        if (
            data != ""
            and isinstance(data, dict)
            and data.get("type")
            and data.get("code")
            and data.get("description")
            and data.get("result")
            and data.get("type").find("success") != -1
            and data.get("description").find("instrument data") != -1
        ):
            with open(f"csv/{exchange}.csv", "w") as file:
                if exchange[-2:].find("CM") != -1:
                    file.write((CM_HDR + data["result"]).replace("|", ","))  # noqa E501
                else:
                    file.write(
                        FO_HDR.replace("|", ",")
                        + "\n".join(
                            lines[: find_nth(lines, ",", 17)]
                            + ",0,0"
                            + lines[find_nth(lines, ",", 17) :]
                            if lines.count(",") == 20
                            else lines[: find_nth(lines, ",", 14)]  # noqa E501
                            + ",-1,,,0,0"
                            + lines[find_nth(lines, ",", 14) :]
                            if lines.count(",") == 17
                            else lines
                            for lines in data["result"].replace("|", ",").split("\n")
                        )
                    )
    for exchange, data in exchange_wise_MC_Idx.items():
        if (
            data != ""
            and isinstance(data, dict)
            and data.get("type")
            and data.get("code")
            and data.get("description")
            and data.get("result")
            and data.get("type").find("success") != -1
            and data.get("description").find("Index List successfully")  # noqa E501
            != -1
        ):
            with open(f"csv/{exchange}_INDEX.csv", "w") as file:
                file.write(
                    (
                        "Name,InstrumentID\n"
                        + "\n".join(
                            index.replace("_", ",")
                            for index in data.get("result").get(
                                "indexList"
                            )  # noqa E501
                        )
                    )
                )  # noqa E501

