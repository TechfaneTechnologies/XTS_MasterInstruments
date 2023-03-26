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

import requests

from json import JSONDecodeError

HEADERS = {"Content-Type": "application/json"}
URL = "https://developers.symphonyfintech.in/marketdata/instruments/master"

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
    with requests.session() as session:
        for exchange in exchangeSegmentList:
            response = session.post(
                URL,
                headers=HEADERS,
                json=dict(exchangeSegmentList=[exchange]),  # noqa E501
            )
            if response.status_code == 200:
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
                    if (
                        data.get("type")
                        and data.get("code")
                        and data.get("description")
                        and data.get("result")
                        and data.get("type").find("success") != -1
                        and data.get("code").find("s-instrument-0010") != -1
                        and data.get("description").find("instrument data") != -1
                    ):
                        with open(f"{exchange}.csv", "w") as file:
                            if exchange[-2:].find("CM") != -1:
                                file.write(
                                    (CM_HDR + data["result"]).replace("|", ",")
                                )  # noqa E501
                            else:
                                file.write(
                                    FO_HDR.replace("|", ",")
                                    + "\n".join(
                                        lines[: find_nth(lines, ",", 17)]
                                        + ",0,0"
                                        + lines[find_nth(lines, ",", 17) :]
                                        if lines.count(",") == 20
                                        else lines[
                                            : find_nth(lines, ",", 14)
                                        ]  # noqa E501
                                        + ",-1,,,0,0"
                                        + lines[find_nth(lines, ",", 14) :]
                                        if lines.count(",") == 17
                                        else lines
                                        for lines in data["result"]
                                        .replace("|", ",")
                                        .split("\n")
                                    )
                                )
