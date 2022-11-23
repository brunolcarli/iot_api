from collections import Counter
from datetime import datetime
import pandas as pd
import pytz


def hour_relative_freq(transmissions, period):
    data = []
    for tx in transmissions:
        dt = datetime.fromtimestamp(tx.timestamp_origin).astimezone(
            pytz.timezone('America/Sao_Paulo')
        )
        data.append([
            dt,
            tx.ldr_sensor,
            tx.temperature_sensor,
            tx.pressure,
            tx.moisture
        ])

    # set up dataframe
    df = pd.DataFrame(data, columns=['DATETIME', 'LDR', 'TEMP', 'PRES', 'MOIS'])
    df = df.set_index(df['DATETIME'])

    df['HOUR'] = df.index.round(freq=period).strftime('%H:'+'%M')
    df['F'] = df.HOUR.value_counts(normalize=True)

    # calculate sensor value differences
    df['LDR_DIFF'] = df.LDR.diff().fillna(0)
    df['TEMP_DIFF'] = df.TEMP.diff().fillna(0)
    df['PRES_DIFF'] = df.PRES.diff().fillna(0)
    df['MOIS_DIFF'] = df.MOIS.diff().fillna(0)

    # group diff sums by time
    df = df[['LDR_DIFF', 'TEMP_DIFF', 'PRES_DIFF', 'MOIS_DIFF', 'HOUR', 'F']].groupby('HOUR').sum()

    # calculate the relative frequency
    df['LDR_REL_FREQ'] = df['LDR_DIFF'] / df.LDR_DIFF.sum()
    df['TEMP_REL_FREQ'] = df['TEMP_DIFF'] / df.TEMP_DIFF.sum()
    df['PRES_REL_FREQ'] = df['PRES_DIFF'] / df.PRES_DIFF.sum()
    df['MOIS_REL_FREQ'] = df['MOIS_DIFF'] / df.MOIS_DIFF.sum()

    # caulcutae positive and negative deviations
    df['LDR_POS_STD'] = df[['LDR_REL_FREQ', 'F']].T.var() + (df.LDR_REL_FREQ + df[['LDR_REL_FREQ', 'F']].T.std())
    df['LDR_NEG_STD'] = df[['LDR_REL_FREQ', 'F']].T.var() + (df.LDR_REL_FREQ - df[['LDR_REL_FREQ', 'F']].T.std())

    df['TEMP_POS_STD'] = df[['TEMP_REL_FREQ', 'F']].T.var() + (df.TEMP_REL_FREQ + df[['TEMP_REL_FREQ', 'F']].T.std())
    df['TEMP_NEG_STD'] = df[['TEMP_REL_FREQ', 'F']].T.var() + (df.TEMP_REL_FREQ - df[['TEMP_REL_FREQ', 'F']].T.std())

    df['PRES_POS_STD'] = df[['PRES_REL_FREQ', 'F']].T.var() + (df.PRES_REL_FREQ + df[['PRES_REL_FREQ', 'F']].T.std())
    df['PRES_NEG_STD'] = df[['PRES_REL_FREQ', 'F']].T.var() + (df.PRES_REL_FREQ - df[['PRES_REL_FREQ', 'F']].T.std())

    df['MOIS_POS_STD'] = df[['MOIS_REL_FREQ', 'F']].T.var() + (df.MOIS_REL_FREQ + df[['PRES_REL_FREQ', 'F']].T.std())
    df['MOIS_NEG_STD'] = df[['MOIS_REL_FREQ', 'F']].T.var() + (df.MOIS_REL_FREQ - df[['PRES_REL_FREQ', 'F']].T.std())

    df[['LDR_REL_FREQ', 'LDR_POS_STD', 'LDR_NEG_STD']] = (df[['LDR_REL_FREQ', 'LDR_POS_STD', 'LDR_NEG_STD']].clip(0)) * 100
    df[['TEMP_REL_FREQ', 'TEMP_POS_STD', 'TEMP_NEG_STD']] = (df[['TEMP_REL_FREQ', 'TEMP_POS_STD', 'TEMP_NEG_STD']].clip(0)) * 100
    df[['PRES_REL_FREQ', 'PRES_POS_STD', 'PRES_NEG_STD']] = (df[['PRES_REL_FREQ', 'PRES_POS_STD', 'PRES_NEG_STD']].clip(0)) * 100
    df[['MOIS_REL_FREQ', 'MOIS_POS_STD', 'MOIS_NEG_STD']] = (df[['MOIS_REL_FREQ', 'MOIS_POS_STD', 'MOIS_NEG_STD']].clip(0)) * 100

    return df.fillna(0).round(2)
